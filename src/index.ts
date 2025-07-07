import 'dotenv/config';
import Fastify from 'fastify';
import { routes } from '@/routes';
import { init } from '@/db/init';

const main = async () => {
    const fastify = Fastify({ logger: true })

    fastify.register(routes, { prefix: '/' })
    fastify.setNotFoundHandler(async (_req, res) => res.status(404).send('Not found'))

    fastify.listen({
        host: process.env.APP_HOST || '0.0.0.0',
        port: parseInt(process.env.APP_PORT || '3000'),
    }, (err, _address) => {
        if (err) throw err
        fastify.log.info(`Server ready!`)
    })

    const dbError = await init()
    if (dbError.error) {
        fastify.log.error(dbError);
        process.exit(1);
    }
}

main()
