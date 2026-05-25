import { defineCollection, z } from 'astro:content';

const recipes = defineCollection({
  type: 'content',
  schema: ({ image }) => z.object({
    title: z.string(),
    subtitle: z.string(),
    tier: z.string(),
    tierOrder: z.number(),
    tierColor: z.string(),
    difficultyText: z.string(),
    totalTime: z.string(),
    recipeSlug: z.string(),
    recipeNumber: z.number(),
    illustration: image().optional(),
  }),
});

export const collections = { recipes };
