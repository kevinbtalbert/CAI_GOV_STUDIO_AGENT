from cmlapi import CMLServiceApi
import cmlapi
import os

from studio.consts import AGENT_STUDIO_SERVICE_APPLICATION_NAME
from studio.cross_cutting.utils import get_appliction_by_name
from studio.db.dao import AgentStudioDao
from studio.api import *
import time

import subprocess

import subprocess
import re


SEMVER_REGEX = re.compile(
    r"^v?(\d+)\.(\d+)\.(\d+)(?:-[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*)?$"
    # Explanation:
    #  v?        -> optional leading 'v' (e.g. v1.2.3)
    # (\d+)\.(\d+)\.(\d+) -> major.minor.patch, each numeric
    # (?:-...)   -> optional pre-release component
)


def git_fetch():
    """
    Fetches changes from the remote (including tags).
    """
    subprocess.run(["git", "fetch", "--tags"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)


def _stash_pop_safely():
    """
    Helper function to pop the stash without blowing up the entire process if there's no stash.
    """
    try:
        subprocess.run(["git", "stash", "pop"], check=True)
    except subprocess.CalledProcessError as e:
        # In case there's no stash or conflicts occur
        print(f"Error popping stashed changes: {e}")


def is_on_a_semantic_version_tag():
    """
    Returns True if HEAD is currently checked out at a tag
    that looks like a semantic version (v1.2.3, etc.).
    """
    try:
        # git describe --tags --exact-match fails (non-zero) if HEAD is not exactly on a tag
        tag = subprocess.run(
            ["git", "describe", "--tags", "--exact-match", "HEAD"],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        ).stdout.strip()

        # Validate with simple semantic-version regex
        return bool(SEMVER_REGEX.match(tag))
    except subprocess.CalledProcessError:
        return False


def get_local_semantic_version():
    """
    Returns the tag name (e.g. 'v1.2.3') if we are indeed on a semantic version tag.
    If HEAD is not exactly on a tag, this method may raise an exception or return None.
    """
    # If not on a tag, this raises CalledProcessError
    tag = subprocess.run(
        ["git", "describe", "--tags", "--exact-match", "HEAD"],
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    ).stdout.strip()

    # Optional sanity check: ensure it matches the SEMVER_REGEX
    # Otherwise raise an error or return None
    if not SEMVER_REGEX.match(tag):
        raise ValueError(f"Current tag '{tag}' is not a valid semantic version.")

    return tag


def get_remote_most_recent_semantic_version():
    """
    Fetches the tag references from 'origin', parses them as semantic versions,
    and returns the highest tag (e.g. 'v1.2.3') by semantic version order.
    If no valid semantic tags exist, returns None.
    """
    # Grab tags from origin; each line looks like:
    #   <commit-hash>  refs/tags/<tagname>
    #
    # For annotated tags, you might see an additional line for ^{} references. We'll skip those.
    tags_output = subprocess.run(
        ["git", "ls-remote", "--tags", "origin"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
    ).stdout.strip()

    # Parse out only valid semantic versions
    valid_versions = []
    for line in tags_output.splitlines():
        commit_hash, ref = line.split()
        # For example, ref == "refs/tags/v1.2.3"
        tagname = ref.replace("refs/tags/", "")

        # Skip "tag^{}" lines
        if "^{}" in tagname:
            continue

        # Check if the tag is a valid semver
        if SEMVER_REGEX.match(tagname):
            valid_versions.append(tagname)

    if not valid_versions:
        return None

    # Sort versions by major/minor/patch so we can pick the highest
    # We can do a naive approach here by splitting on '.' and comparing, or use the same regex captures
    # For a robust approach, parse into (major, minor, patch) and compare as tuples.
    def parse_semver_str(v):
        m = SEMVER_REGEX.match(v)
        # group(1)=major, group(2)=minor, group(3)=patch
        return tuple(map(int, m.groups()[:3]))  # ignore pre-release for a straightforward approach

    valid_versions.sort(key=lambda ver: parse_semver_str(ver))
    most_recent = valid_versions[-1]

    return most_recent


def is_on_main_branch():
    """
    Returns True if the current (local) branch is 'main'.
    """
    branch = subprocess.run(
        ["git", "rev-parse", "--abbrev-ref", "HEAD"],
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    ).stdout.strip()
    return branch == "main"


def get_local_commit():
    """
    Returns the commit hash currently checked out locally (HEAD).
    """
    return subprocess.run(
        ["git", "rev-parse", "HEAD"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
    ).stdout.strip()


def get_remote_head_commit():
    """
    Returns the commit hash of the HEAD of the tracked remote branch.
    For simplicity, assume the current local branch is tracking origin/<branch>.
    If you're specifically targeting 'main', you can hardcode 'origin/main' instead.
    """
    branch = subprocess.run(
        ["git", "rev-parse", "--abbrev-ref", "HEAD"],
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    ).stdout.strip()

    remote_branch = f"origin/{branch}"
    return subprocess.run(
        ["git", "rev-parse", remote_branch], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
    ).stdout.strip()


def check_studio_upgrade_status(
    request: CheckStudioUpgradeStatusRequest, cml: CMLServiceApi = None, dao: AgentStudioDao = None
) -> CheckStudioUpgradeStatusResponse:
    """
    Compares either the local semantic version vs. the most recent remote version
    OR the local commit vs. the remote HEAD commit (for main or other branches).
    """
    # 1) Fetch from remote
    git_fetch()

    # 2) Decide which type of versioning to compare
    if is_on_a_semantic_version_tag():
        # If we are on a semantic version, only upgrade on official releases
        local_version = get_local_semantic_version()
        newest_version = get_remote_most_recent_semantic_version() or local_version
    elif is_on_main_branch():
        # If on main, we just track commits
        local_version = get_local_commit()
        newest_version = get_remote_head_commit()
    else:
        # For any development branch that is not main, also track commits
        local_version = get_local_commit()
        newest_version = get_remote_head_commit()

    return CheckStudioUpgradeStatusResponse(
        local_version=local_version,
        newest_version=newest_version,
    )


def upgrade_studio(
    request: UpgradeStudioRequest, cml: CMLServiceApi = None, dao: AgentStudioDao = None
) -> UpgradeStudioResponse:
    """
    If currently on a semantic version tag, fetch remote tags and checkout the newest semantic version tag.
    Otherwise, do a normal stash/pull/stash pop flow.
    In both cases, stash/pop is used to preserve local changes.
    """

    # Always stash before doing any git operation, so we can safely switch versions/branches
    try:
        subprocess.run(["git", "stash"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error stashing changes: {e}")

    if is_on_a_semantic_version_tag():
        try:
            # 1) Fetch remote so we get the latest tags
            git_fetch()

            # 2) Get the newest remote semantic version tag
            newest_tag = get_remote_most_recent_semantic_version()
            if not newest_tag:
                print("No valid semantic tags exist on remote.")
                # Attempt to pop stash so you’re not left with stashed changes
                _stash_pop_safely()
                return UpgradeStudioResponse()

            # 3) Checkout that tag
            subprocess.run(["git", "checkout", newest_tag], check=True)
            print(f"Checked out newest semantic version tag: {newest_tag}")
        except subprocess.CalledProcessError as e:
            print(f"Error upgrading to latest semantic version tag: {e}")
            _stash_pop_safely()
            return UpgradeStudioResponse()
    else:
        # If not on semantic version, do a normal 'git pull'
        try:
            subprocess.run(["git", "pull"], check=True)
        except subprocess.CalledProcessError as e:
            print(f"Error pulling changes: {e}")
            _stash_pop_safely()
            return UpgradeStudioResponse()

    # Pop the stash to restore local changes
    _stash_pop_safely()

    # Also run any and all DB default upgrades. Our upgrades need to be compatible with our
    # style of project defaults here - which means that if project defaults gets updated with
    # new schemas, then alembic still needs to go through the entire ugrade lineage even though
    # the new schemas alredy exist. This is to support both old users and new users of agent studio.
    # This means that, for example, if there was an alembic version upgrade to add a column, we need
    # to first check if that column already exists. If the column already exists, someone new must have
    # pulled down agent studio and ran a fresh project-defaults. If the column does not exist, that
    # means we are performing an upgrade.
    try:
        subprocess.run(["uv", "run", "alembic", "upgrade", "head"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error upgrading DB: {e}")

    # Also perform any project default upgrades necessary. Note this will explicitly
    # check to see if an existing project default has already been added to make sure
    # that we are not duplicating project defaults.
    try:
        subprocess.run(["uv", "run", "bin/initialize-project-defaults.py"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error initializing project defaults: {e}")

    # Install new dependencies
    try:
        subprocess.run(["npm", "install"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running npm install: {e}")

    # Rebuild frontend app
    try:
        subprocess.run(["npm", "run", "build"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running npm run build: {e}")

    # Run post upgrade hook
    try:
        subprocess.run(["uv", "run", "bin/post-upgrade-hook.py"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running post upgrade: {e}")

    # Small sleep to ensure output from post-upgrade-hook makes it
    # to application logs. Not necessary functionally, but will help
    # with diagnostics.
    time.sleep(10)

    # Restart the application
    restart_studio_application(RestartStudioApplicationRequest(), cml=cml, dao=dao)

    # Restart the application.
    return UpgradeStudioResponse()


def restart_studio_application(
    request: RestartStudioApplicationRequest, cml: CMLServiceApi = None, dao: AgentStudioDao = None
) -> RestartStudioApplicationResponse:
    # Grab a reference to the current application
    application: cmlapi.Application = get_appliction_by_name(cml=cml, name=AGENT_STUDIO_SERVICE_APPLICATION_NAME)

    # Restart the application
    cml.restart_application(os.getenv("CDSW_PROJECT_ID"), application.id)

    # NOTE: this will technically never be returned to the
    # frontend because we are sending a command to restart
    # the application, which means the pod that is running
    # this command will be killed.
    return RestartStudioApplicationResponse()
