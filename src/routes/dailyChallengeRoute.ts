import  { Router, Request, Response } from 'express';
import dailyChallengeService from '../services/dailyChallengeService';

const router: Router = Router();

router.get('/dailyChallenge', async (req: Request, res: Response) => {
  try {
    const dailyChallenge = await dailyChallengeService.getDailyChallenge();
    res.json(dailyChallenge);
  } catch (error) {
    res.status(500).json({ error: 'Failed to fetch daily challenge!' });
  }
});

export default router;