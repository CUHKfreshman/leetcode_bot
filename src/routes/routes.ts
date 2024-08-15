import { Application } from 'express';
import fs from 'fs';
import path from 'path';

export function loadRoutes(app: Application): void {
    const routeFiles = fs.readdirSync(__dirname).filter(file => file.endsWith('.ts') || file.endsWith('.js'));

    routeFiles.forEach(file => {
        // skip this file
        if (file.split('.')[0] === 'routes') {
            return;
        }
        const route = require(path.join(__dirname, file));
        // camelCase to kebab-case
        const convertedRouteName = file.split('.')[0].slice(0,-5).replace(/([a-z0-9]|(?=[A-Z]))([A-Z])/g, '$1-$2').toLowerCase();
        console.log(`Loading route: ${convertedRouteName}`);
        if (convertedRouteName === 'ping') {
            app.use('/', route.default);
        } else {
            app.use(`/api`, route.default);
        }
    });
}