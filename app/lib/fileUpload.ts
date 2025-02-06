export async function uploadFile(
  file: File,
  setUploading?: (uploading: boolean) => void,
): Promise<string> {
  try {
    setUploading?.(true);

    // Read file as array buffer and convert to base64
    const arrayBuffer = await file.arrayBuffer();
    const bytes = new Uint8Array(arrayBuffer);
    const base64Content = btoa(String.fromCharCode(...bytes));

    const response = await fetch('/api/grpc/nonStreamingTemporaryFileUpload', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        full_content: base64Content,
        file_name: file.name,
      }),
    });

    if (!response.ok) {
      throw new Error(`Upload failed: ${response.statusText}`);
    }

    const result = await response.json();
    return result.file_path;
  } catch (error) {
    console.error('Error uploading file:', error);
    throw error;
  } finally {
    setUploading?.(false);
  }
}
