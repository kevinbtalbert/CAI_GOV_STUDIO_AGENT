import { DownloadTemporaryFileRequest } from '@/studio/proto/agent_studio';
/**
 * Downloads a file from the server using the downloadTemporaryFile API
 *
 * @param filePath - The path of the file to download
 * @param setDownloading - Optional callback to track download state
 * @returns A Promise that resolves to a File object
 */
export async function downloadFile(
  filePath: string,
  setDownloading?: (downloading: boolean) => void,
): Promise<File> {
  try {
    setDownloading?.(true);

    const request: DownloadTemporaryFileRequest = {
      file_path: filePath,
    };

    const response = await fetch('/api/grpc/downloadTemporaryFile', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request),
    });

    if (!response.ok) {
      throw new Error(`Download failed: ${response.statusText}`);
    }

    // Get the file data as an array buffer
    const arrayBuffer = await response.arrayBuffer();

    // Get the filename from the response headers or use a default
    const contentDisposition = response.headers.get('Content-Disposition');
    let filename = 'downloaded-file';
    if (contentDisposition) {
      const filenameMatch = contentDisposition.match(/filename="?([^"]+)"?/);
      if (filenameMatch && filenameMatch[1]) {
        filename = filenameMatch[1];
      }
    } else {
      // If no filename in headers, try to extract from the file path
      const pathParts = filePath.split('/');
      if (pathParts.length > 0 && pathParts[pathParts.length - 1]) {
        filename = pathParts[pathParts.length - 1];
      }
    }

    // Create a File object from the array buffer
    const file = new File([arrayBuffer], filename, {
      type: response.headers.get('Content-Type') || 'application/octet-stream',
    });

    return file;
  } catch (error) {
    console.error('Error downloading file:', error);
    throw error;
  } finally {
    setDownloading?.(false);
  }
}

/**
 * Triggers a browser download for a File object
 *
 * @param file - The File object to download
 */
export function saveFileToDevice(file: File): void {
  // Create a URL for the file
  const url = URL.createObjectURL(file);

  // Create a temporary anchor element
  const a = document.createElement('a');
  a.href = url;
  a.download = file.name;

  // Append to the document, click it, and remove it
  document.body.appendChild(a);
  a.click();

  // Clean up
  setTimeout(() => {
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  }, 0);
}

/**
 * Downloads a file and saves it to the device in one operation
 *
 * @param filePath - The path of the file to download
 * @param setDownloading - Optional callback to track download state
 * @returns A Promise that resolves when the download is complete
 */
export async function downloadAndSaveFile(
  filePath: string,
  setDownloading?: (downloading: boolean) => void,
): Promise<void> {
  try {
    const file = await downloadFile(filePath, setDownloading);
    saveFileToDevice(file);
  } catch (error) {
    console.error('Error downloading and saving file:', error);
    throw error;
  }
}
