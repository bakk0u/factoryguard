import type { FastifyInstance } from "fastify";

// Await the API lifecycle, not an assumed laptop-speed polling count. The
// application's 60-second deadline and every terminal-state assertion stay intact.
export async function waitForInvestigation(app: FastifyInstance, id: string) {
  const deadline = performance.now() + 60000;
  while (performance.now() < deadline) {
    const response = await app.inject(`/api/investigations/${encodeURIComponent(id)}`);
    const state = response.json();
    if (state.status !== "running") return state;
    await new Promise(resolve => setTimeout(resolve, 20));
  }
  throw Error("Investigation did not reach a terminal state within the request deadline");
}
