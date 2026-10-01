/** Server-side SDK. Never put a project API key in client-side browser bundles. */
export type NexusRun = {
  run_id: string;
  project_id: string;
  /** REST v1 compatibility field. Product terminology is Guardian. */
  agent: 'general' | 'builder' | 'research';
  goal: string;
  status: 'completed' | 'pending_approval' | 'failed' | 'max_steps';
  answer: string | null;
  steps_used: number;
  events: Record<string, unknown>[];
  pending_approval: Record<string, unknown> | null;
};

export type IntelligencePlan = {
  kind: string;
  confidence: number;
  uncertainty: number;
  capabilities: string[];
  required_tools: string[];
  strategy: string;
  strategy_rationale: string[];
  required_evidence: string[];
  adversarial_cases: Record<string, string>[];
  assumptions: string[];
};

export type MissionPlan = {
  kind: string;
  confidence: number;
  capabilities: string[];
  required_tools: string[];
  selected_guardians: string[];
  missing_capabilities: string[];
  missing_tools: string[];
  blocked_tools: string[];
  sufficient: boolean;
  reasons: string[];
};

export type IntegrationReadiness = {
  integration: string;
  description: string;
  connected: boolean;
  required_capabilities: string[];
  required_tools: string[];
  missing_capabilities: string[];
  missing_tools: string[];
  ready: boolean;
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
    if (!response.ok) throw new Error(`Nexus Starship Guardians request failed: ${response.status}`);
    return (await response.json()) as T;
  }

  /** REST v1 retains the wire field `agent`; callers should treat it as the Guardian selector. */
  createRun(projectId: string, goal: string, agent: NexusRun['agent'] = 'general') {
    return this.request<NexusRun>(`/v1/projects/${encodeURIComponent(projectId)}/runs`, {
      method: 'POST', body: JSON.stringify({ goal, agent }),
    });
  }

  planIntelligence(projectId: string, goal: string) {
    return this.request<IntelligencePlan>(
      `/v1/projects/${encodeURIComponent(projectId)}/intelligence-plan`,
      { method: 'POST', body: JSON.stringify({ goal }) },
    );
  }

  planMission(projectId: string, goal: string) {
    return this.request<MissionPlan>(`/v1/projects/${encodeURIComponent(projectId)}/mission-plan`, {
      method: 'POST', body: JSON.stringify({ goal }),
    });
  }

  integrationReadiness(projectId: string, integrationName: string) {
    return this.request<IntegrationReadiness>(
      `/v1/projects/${encodeURIComponent(projectId)}/integrations/${encodeURIComponent(integrationName)}/readiness`,
    );
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
