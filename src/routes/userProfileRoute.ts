import { Router, Request, Response } from 'express';
import userProfileService from '../services/userProfileService';

const router: Router = Router();

router.get('/user/:username', async (req: Request, res: Response) => {
  try {
    const { username } = req.params;
    const userProfile = await userProfileService.getUserProfile(username);
    res.json(userProfile);
  } catch (error) {
    res.status(500).json({ error: 'Failed to fetch user profile' });
  }
});

export default router;