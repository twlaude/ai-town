/**
 * External API to inject memories into AI Town agents.
 * Used to sync OpenClaw bot activity logs into AI Town.
 *
 * Usage from CLI:
 *   npx convex run injectMemory:inject '{"playerName":"Atlas","description":"오늘 ghost_catcher CLIP→GPT 비전 마이그레이션을 완료했다.","importance":7}'
 */
import { v } from 'convex/values';
import { action, internalQuery } from './_generated/server';
import { internal } from './_generated/api';
import { fetchEmbedding } from './util/llm';
import { GameId } from './aiTown/ids';

export const inject = action({
  args: {
    playerName: v.string(), // "Atlas", "Critic", or "Builder"
    description: v.string(), // Memory text
    importance: v.optional(v.number()), // 0-10, default 5
  },
  handler: async (ctx, args) => {
    // Find the player and agent by name
    const result = await ctx.runQuery(internal.injectMemory.findAgent, {
      playerName: args.playerName,
    });
    if (!result) {
      throw new Error(`Player "${args.playerName}" not found in any active world`);
    }

    // Generate embedding for the memory
    const { embedding } = await fetchEmbedding(args.description);

    // Insert the memory
    await ctx.runMutation(internal.agent.memory.insertMemory, {
      agentId: result.agentId as GameId<'agents'>,
      playerId: result.playerId,
      description: args.description,
      importance: args.importance ?? 5,
      lastAccess: Date.now(),
      data: {
        type: 'reflection',
        relatedMemoryIds: [],
      },
      embedding,
    });

    return { success: true, playerName: args.playerName, description: args.description };
  },
});

export const findAgent = internalQuery({
  args: {
    playerName: v.string(),
  },
  handler: async (ctx, args) => {
    const worldStatus = await ctx.db
      .query('worldStatus')
      .filter((q) => q.eq(q.field('isDefault'), true))
      .first();
    if (!worldStatus) return null;

    const world = await ctx.db.get(worldStatus.worldId);
    if (!world) return null;

    // Find player by name via playerDescriptions
    const descriptions = await ctx.db
      .query('playerDescriptions')
      .withIndex('worldId', (q) => q.eq('worldId', worldStatus.worldId))
      .collect();

    const playerDesc = descriptions.find(
      (d) => d.name.toLowerCase() === args.playerName.toLowerCase(),
    );
    if (!playerDesc) return null;

    const agent = world.agents.find((a) => a.playerId === playerDesc.playerId);
    if (!agent) return null;

    return {
      playerId: playerDesc.playerId,
      agentId: agent.id,
      worldId: worldStatus.worldId,
    };
  },
});
