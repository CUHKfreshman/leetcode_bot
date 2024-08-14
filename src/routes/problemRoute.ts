import { Router, Request, Response } from 'express';
import ProblemService from '../services/problemService';

const router: Router = Router();

router.get('/problem/:id?', async (req: Request, res: Response) => {
    try {
        const problemService = await ProblemService.getInstance();
        const id = req.params.id ? parseInt(req.params.id) : undefined;
        const problem = await problemService.getProblem(id);
        if (problem) {
            res.json(problem);
        } else {
            res.status(404).json({ error: 'Problem not found' });
        }
    } catch (error) {
        res.status(500).json({ error: 'Failed to fetch problem' });
    }
});

export default router;