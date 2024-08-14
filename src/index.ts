import dotenv from 'dotenv';
import express, { Application } from 'express';
import { loadRoutes } from './routes/routes';

if (process.env.NODE_ENV === 'production') {
  dotenv.config({ path: '.env.production' });
} else {
  dotenv.config({ path: '.env.development' });
}

const app: Application = express();
const port: number = parseInt(process.env.PORT || '3000', 10);

loadRoutes(app);

app.listen(port, () => {
  console.log(`My uwu server is running in ${process.env.NODE_ENV} mode on port ${port}`);
});