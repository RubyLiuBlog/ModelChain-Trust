type HttpMethod = "GET" | "POST" | "PUT" | "PATCH" | "DELETE";

interface RequestConfig {
  headers?: Record<string, string>;
  params?: Record<string, string | number>;
  signal?: AbortSignal;
  isFormData?: boolean;
}

export interface CommonResponse<T = unknown> {
  success: boolean;
  message: string;
  data: T;
}
class HttpClient {
  private baseURL: string;
  private defaultHeaders: Record<string, string>;

  constructor(baseURL: string = "", headers: Record<string, string> = {}) {
    this.baseURL = baseURL;
    this.defaultHeaders = {
      "Content-Type": "application/json",
      ...headers,
    };
  }

  private async request<T>(
    method: HttpMethod,
    endpoint: string,
    data?: unknown,
    config?: RequestConfig
  ): Promise<T> {
    const url = new URL(`${this.baseURL}${endpoint}`);

    // 处理查询参数
    if (config?.params) {
      Object.entries(config.params).forEach(([key, value]) => {
        url.searchParams.append(key, String(value));
      });
    }

    const headers = {
      ...this.defaultHeaders,
      ...config?.headers,
    };

    try {
      const response = await fetch(url.toString(), {
        method,
        headers,
        body: data ? JSON.stringify(data) : undefined,
        signal: config?.signal,
      });

      // 处理HTTP错误状态
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      // 尝试解析JSON
      try {
        return (await response.json()) as T;
      } catch (error) {
        // 处理空响应
        return null as T;
      }
    } catch (error) {
      // 统一错误处理
      console.error("Request failed:", error);
      throw error;
    }
  }

  public get<T>(endpoint: string, config?: RequestConfig) {
    return this.request<T>("GET", endpoint, undefined, config);
  }

  public post<T>(endpoint: string, data: unknown, config?: RequestConfig) {
    return this.request<T>("POST", endpoint, data, config);
  }

  public put<T>(endpoint: string, data: unknown, config?: RequestConfig) {
    return this.request<T>("PUT", endpoint, data, config);
  }

  public patch<T>(endpoint: string, data: unknown, config?: RequestConfig) {
    return this.request<T>("PATCH", endpoint, data, config);
  }

  public delete<T>(endpoint: string, config?: RequestConfig) {
    return this.request<T>("DELETE", endpoint, undefined, config);
  }
}

// 示例实例（根据项目需要配置）
export const API = new HttpClient(
  process.env.NEXT_PUBLIC_API_BASE_URL || "/api",
  {
    Authorization: `Bearer ${sessionStorage.getItem("token") || ""}`,
  }
);
