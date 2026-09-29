/** Server-side SDK. Never put a project API key in client-side browser bundles. */
export type NexusRun = {
  run_id: string;
  project_id: string;
  agent: 'general' | 'builder' | 'research';
  goal: string;
  status: 'completed' | 'pending_approval' | 'failed' | 'max_steps';
  answer: string | null;
  steps_used: number;
  events: Record<string, unknown>[];
  pending_approval: Record<string, unknown> | null;
};

export class NexusClient {
  constructor(private readonly baseUrl: string, private readonly apiKey: string) {}

  private async request<T>(path: string, init: RequestInit = {}): Promise<T> {
    const response = await fetch(`${this.baseUrl.replace(/\/$/, '')}${path}`, {
      ...init,
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${this.apiKey}`,
        ...init.headers,
      },
    });
    if (!response.ok) throw new Error(`NEXUS request failed: ${response.status}`);
    return (await response.json()) as T;
  }

  createRun(projectId: string, goal: string, agent: NexusRun['agent'] = 'general') {
    return this.request<NexusRun>(`/v1/projects/${encodeURIComponent(projectId)}/runs`, {
      method: 'POST', body: JSON.stringify({ goal, agent }),
    });
  }

  getRun(runId: string) {
    return this.request<NexusRun>(`/v1/runs/${encodeURIComponent(runId)}`);
  }

  approve(runId: string, approved: boolean) {
    return this.request<NexusRun>(`/v1/runs/${encodeURIComponent(runId)}/approval`, {
      method: 'POST', body: JSON.stringify({ approved }),
    });
  }
}
