import { Router, Request, Response } from 'express';
import pingService from '../services/pingService';

const router: Router = Router();

router.get('/ping', async (req: Request, res: Response) => {
  try {
    const result: string = await pingService.getPongResponse();
    res.send(result);
  } catch (error) {
    res.status(500).send('An error occurred');
  }
});

export default router;  // This line is correct now!