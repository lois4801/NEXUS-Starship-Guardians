/** Example server-only integration route pseudo-handler; adapt to Ember's real framework/auth. */
import { NexusClient } from '../sdk/typescript/src/client';

export async function runEmberAgent(user: { id: string; canUseAgents: boolean }, goal: string) {
  if (!user.canUseAgents) throw new Error('Not authorized');
  const baseUrl = process.env.NEXUS_URL;
  const apiKey = process.env.NEXUS_EMBER_PROJECT_KEY;
  if (!baseUrl || !apiKey) throw new Error('Missing server-side NEXUS configuration');
  return new NexusClient(baseUrl, apiKey).createRun('ember-dev', goal, 'builder');
}
