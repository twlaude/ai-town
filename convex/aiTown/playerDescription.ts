import { ObjectType, v } from 'convex/values';
import { GameId, parseGameId, playerId } from './ids';

export const serializedPlayerDescription = {
  playerId,
  name: v.string(),
  description: v.string(),
  character: v.string(),
  gone: v.optional(v.boolean()),
};
export type SerializedPlayerDescription = ObjectType<typeof serializedPlayerDescription>;

export class PlayerDescription {
  playerId: GameId<'players'>;
  name: string;
  description: string;
  character: string;
  gone: boolean;

  constructor(serialized: SerializedPlayerDescription) {
    const { playerId, name, description, character, gone } = serialized;
    this.playerId = parseGameId('players', playerId);
    this.name = name;
    this.description = description;
    this.character = character;
    this.gone = gone ?? false;
  }

  serialize(): SerializedPlayerDescription {
    const { playerId, name, description, character, gone } = this;
    return {
      playerId,
      name,
      description,
      character,
      gone,
    };
  }
}
