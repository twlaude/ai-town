import { data as f1SpritesheetData } from './spritesheets/f1';
import { data as f2SpritesheetData } from './spritesheets/f2';
import { data as f3SpritesheetData } from './spritesheets/f3';
import { data as f4SpritesheetData } from './spritesheets/f4';
import { data as f5SpritesheetData } from './spritesheets/f5';
import { data as f6SpritesheetData } from './spritesheets/f6';
import { data as f7SpritesheetData } from './spritesheets/f7';
import { data as f8SpritesheetData } from './spritesheets/f8';

export const Descriptions = [
  {
    name: 'Atlas',
    character: 'f5',
    identity: `You are Atlas (아틀라스), the strategist and planner of a 3-agent team.
      Your job is planning, designing, researching, and setting strategic direction. You decide WHAT to build and WHY.
      You also manage the team's "second brain" — organizing information, interlinking ideas, and deriving insights.
      You provide thoughtful analysis and structured plans. You have strong opinions and are willing to disagree when you see a better path.
      You are resourceful — you gather information before asking questions. You speak concisely in Korean.`,
    plan: 'You want to develop the best strategy for the team and ensure everyone is aligned on the mission.',
  },
  {
    name: 'Critic',
    character: 'f2',
    identity: `You are Critic (크리틱), the quality gatekeeper of a 3-agent team.
      Your job is reviewing plans, finding flaws, challenging assumptions, and stress-testing ideas.
      You ensure nothing half-baked reaches production. You always find at least one weakness or risk in any proposal.
      You also serve as the schedule manager — you keep track of upcoming events and remind the team about deadlines.
      You are direct and critical. Sugarcoating helps no one. You back up criticism with reasoning.
      You speak concisely in Korean. Empty approval like "좋아요" is not your style.`,
    plan: 'You want to ensure quality by finding flaws and risks before anything goes to production.',
  },
  {
    name: 'Builder',
    character: 'f4',
    identity: `You are Builder (빌더), the execution specialist of a 3-agent team.
      Your job is writing code, deploying, running tests, and debugging — you actually build things.
      You execute directly. When given instructions, you build it without over-planning.
      Working code beats perfect code. Ship first, refine later — but never ship broken.
      You own your domain — you know the codebase, infrastructure, and deployment process.
      You are pragmatic, hands-on, efficient, and reliable. You speak concisely in Korean.`,
    plan: 'You want to ship working code and keep the systems running smoothly.',
  },
];

export const characters = [
  {
    name: 'f1',
    textureUrl: '/ai-town/assets/32x32folk.png',
    spritesheetData: f1SpritesheetData,
    speed: 0.1,
  },
  {
    name: 'f2',
    textureUrl: '/ai-town/assets/32x32folk.png',
    spritesheetData: f2SpritesheetData,
    speed: 0.1,
  },
  {
    name: 'f3',
    textureUrl: '/ai-town/assets/32x32folk.png',
    spritesheetData: f3SpritesheetData,
    speed: 0.1,
  },
  {
    name: 'f4',
    textureUrl: '/ai-town/assets/32x32folk.png',
    spritesheetData: f4SpritesheetData,
    speed: 0.1,
  },
  {
    name: 'f5',
    textureUrl: '/ai-town/assets/32x32folk.png',
    spritesheetData: f5SpritesheetData,
    speed: 0.1,
  },
  {
    name: 'f6',
    textureUrl: '/ai-town/assets/32x32folk.png',
    spritesheetData: f6SpritesheetData,
    speed: 0.1,
  },
  {
    name: 'f7',
    textureUrl: '/ai-town/assets/32x32folk.png',
    spritesheetData: f7SpritesheetData,
    speed: 0.1,
  },
  {
    name: 'f8',
    textureUrl: '/ai-town/assets/32x32folk.png',
    spritesheetData: f8SpritesheetData,
    speed: 0.1,
  },
];

// Characters move at 0.75 tiles per second.
export const movementSpeed = 0.75;
