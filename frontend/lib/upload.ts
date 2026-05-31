const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

export type UploadProgress = {
  loaded: number;
  total: number;
  percent: number;
  step: "uploading" | "indexing";
  message: string;
};

export const SUPPORTED_UPLOAD_EXTENSIONS = ["pdf"];
export const SUPPORTED_UPLOAD_ACCEPT = ".pdf";

export function uploadDocument(file: File, onProgress?: (progress: UploadProgress) => void): Promise<any> {
  return new Promise((resolve, reject) => {
    const xhr = new XMLHttpRequest();
    const formData = new FormData();
    formData.append("file", file);

    xhr.open("POST", `${API_BASE_URL}/api/v1/papers/upload`);

    let indexingStageSent = false;

    xhr.upload.onprogress = (event) => {
      if (!event.lengthComputable) return;
      const percent = Math.min(100, Math.round((event.loaded / event.total) * 100));
      onProgress?.({
        loaded: event.loaded,
        total: event.total,
        percent,
        step: "uploading",
        message: percent < 100 ? "Uploading document…" : "Finalizing upload…",
      });
    };

    xhr.onreadystatechange = () => {
      if (xhr.readyState === 2 && !indexingStageSent) {
        indexingStageSent = true;
        onProgress?.({
          loaded: file.size,
          total: file.size,
          percent: 100,
          step: "indexing",
          message: "Indexing uploaded document…",
        });
      }
    };

    xhr.onload = () => {
      if (xhr.status >= 200 && xhr.status < 300) {
        try {
          resolve(JSON.parse(xhr.responseText));
        } catch (error) {
          reject(new Error("Invalid upload response."));
        }
      } else {
        const responseText = xhr.responseText;
        try {
          const body = JSON.parse(responseText || "{}");
          reject(new Error(body.detail || body.error || responseText || xhr.statusText));
        } catch {
          reject(new Error(responseText || xhr.statusText));
        }
      }
    };

    xhr.onerror = () => {
      reject(new Error("Upload failed. Please check your connection and try again."));
    };

    onProgress?.({
      loaded: 0,
      total: file.size,
      percent: 0,
      step: "uploading",
      message: "Preparing document upload…",
    });

    xhr.send(formData);
  });
}
