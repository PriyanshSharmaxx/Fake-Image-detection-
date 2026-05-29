const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

export class ApiClient {
  private static getHeaders(token?: string | null): Record<string, string> {
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
    };
    const storedToken = token || (typeof window !== 'undefined' ? localStorage.getItem('token') : null);
    if (storedToken) {
      headers['Authorization'] = `Bearer ${storedToken}`;
    }
    return headers;
  }

  static async request(endpoint: string, options: RequestInit = {}): Promise<any> {
    const url = `${API_URL}${endpoint}`;
    const headers = {
      ...this.getHeaders(),
      ...(options.headers || {}),
    };

    const response = await fetch(url, { ...options, headers });
    if (!response.ok) {
      const errData = await response.json().catch(() => ({}));
      throw new Error(errData.detail || 'Request failed');
    }
    
    if (response.status === 204) return null;
    return response.json();
  }

  /**
   * Upload image directly to S3 and trigger ML pipeline.
   */
  static async uploadAndAnalyze(
    file: File,
    onProgress?: (progress: number) => void
  ): Promise<any> {
    // 1. Get signed upload URL from FastAPI backend
    const uploadPolicy = await this.request('/detections/upload-url', {
      method: 'POST',
      body: JSON.stringify({
        filename: file.name,
        content_type: file.type,
      }),
    });

    // 2. Perform direct upload to S3 using FormData policy fields
    const formData = new FormData();
    Object.entries(uploadPolicy.fields).forEach(([key, value]) => {
      formData.append(key, value as string);
    });
    formData.append('file', file);

    const s3UploadResponse = await fetch(uploadPolicy.url, {
      method: 'POST',
      body: formData,
    });

    if (!s3UploadResponse.ok) {
      throw new Error('Storage upload failed.');
    }

    if (onProgress) onProgress(100);

    // 3. Trigger model analysis
    const analysisResponse = await this.request('/detections/analyze', {
      method: 'POST',
      body: JSON.stringify({
        object_key: uploadPolicy.object_key,
        generate_heatmap: true,
        threshold: 0.5,
      }),
    });

    return analysisResponse;
  }
}
