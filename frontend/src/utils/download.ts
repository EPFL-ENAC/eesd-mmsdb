import JSZip from 'jszip';

export function downloadArrayBuffer(data: ArrayBuffer, filename: string, mimeType: string) {
    const blob = new Blob([data], { type: mimeType });
    const url = URL.createObjectURL(blob);
  
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}

export interface DownloadableFile {
    data: ArrayBuffer | Blob;
    filename: string;
    mimeType: string;
}

// Function to download multiple files in a zip
export async function downloadFilesAsZip(files: DownloadableFile[], zipFilename: string) {
    const zip = new JSZip();
  
    files.forEach(file => {
        zip.file(file.filename, file.data);
    });
  
    const content = await zip.generateAsync({ type: 'blob' });
    const url = URL.createObjectURL(content);
  
    const a = document.createElement('a');
    a.href = url;
    a.download = zipFilename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}