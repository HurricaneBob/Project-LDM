export const personas = [
  {
    id: 'commander',
    name: 'The Commander',
    essence: 'DECISIVE',
    description: 'Takes initiative quickly and provides clear direction under pressure.',
    evaluates: ['Decision-Making', 'Leadership Tendencies', 'Stress Management', 'Execution Speed'],
    colorVar: '--color-persona-commander',
    colorClass: 'text-persona-commander',
    borderColorClass: 'border-persona-commander',
    image: '/personas/commander.png',
    characterScale: 1.0,
    voiceHint: { pitch: 0.9, rate: 1.05 },
  },
  {
    id: 'facilitator',
    name: 'The Facilitator',
    essence: 'COLLABORATIVE',
    description: 'Encourages participation, mediates conflict, and helps maintain positive team dynamics.',
    evaluates: ['Communication Style', 'Conflict Resolution', 'Team Motivation', 'Empathy'],
    colorVar: '--color-persona-facilitator',
    colorClass: 'text-persona-facilitator',
    borderColorClass: 'border-persona-facilitator',
    image: '/personas/facilitator.png',
    characterScale: 0.89,
    voiceHint: { pitch: 1.1, rate: 1.0 },
  },
  {
    id: 'strategist',
    name: 'The Strategist',
    essence: 'ANALYTICAL',
    description: 'Focuses on planning, prioritization, and long-term problem solving.',
    evaluates: ['Analytical Thinking', 'Prioritization', 'Risk Awareness', 'Decision-Making'],
    colorVar: '--color-persona-strategist',
    colorClass: 'text-persona-strategist',
    borderColorClass: 'border-persona-strategist',
    image: '/personas/strategist.png',
    characterScale: 0.81,
    voiceHint: { pitch: 0.95, rate: 0.95 },
  },
  {
    id: 'supporter',
    name: 'The Supporter',
    essence: 'EMPATHETIC',
    description: 'Prioritizes trust, encouragement, and the emotional well-being of the team.',
    evaluates: ['Empathy', 'Emotional Awareness', 'Psychological Safety', 'Inclusive Communication'],
    colorVar: '--color-persona-supporter',
    colorClass: 'text-persona-supporter',
    borderColorClass: 'border-persona-supporter',
    image: '/personas/supporter.png',
    characterScale: 0.91,
    voiceHint: { pitch: 1.15, rate: 0.9 },
  },
  {
    id: 'adaptive',
    name: 'The Adaptive',
    essence: 'FLEXIBLE',
    description: 'Adjusts leadership and communication style depending on the situation and team dynamics.',
    evaluates: ['Cultural Adaptability', 'Communication Flexibility', 'Situational Awareness', 'Conflict Resolution'],
    colorVar: '--color-persona-adaptive',
    colorClass: 'text-persona-adaptive',
    borderColorClass: 'border-persona-adaptive',
    image: '/personas/adaptive.png',
    characterScale: 1.06,
    voiceHint: { pitch: 1.0, rate: 1.0 },
  },
];

// 게임에서 평가하는 전체 파라미터 (페르소나들의 evaluates 합집합)
export const allParameters = [
  'Decision-Making', 'Leadership Tendencies', 'Stress Management', 'Execution Speed',
  'Communication Style', 'Conflict Resolution', 'Team Motivation', 'Empathy',
  'Analytical Thinking', 'Prioritization', 'Risk Awareness',
  'Emotional Awareness', 'Psychological Safety', 'Inclusive Communication',
  'Cultural Adaptability', 'Communication Flexibility', 'Situational Awareness',
];

export const roleOptions = ['Developer', 'Designer', 'PM', 'Founder', 'Marketer', 'Student', 'Other'];
export const pressureOptions = ['Take charge', 'Seek consensus', 'Step back and analyze'];
export const conflictOptions = ['Push back directly', 'Find common ground', 'Ask more questions'];
export const growthAreaOptions = [
  'Conflict management', 'Decision-making', 'Cross-cultural communication',
  'Reading the room', 'Time pressure handling',
];
