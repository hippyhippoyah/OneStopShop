FROM node:latest


WORKDIR /user/src/app


COPY ./package.json .
COPY ./yarn.lock ./


RUN npm install


COPY . .
RUN npm run build

EXPOSE 3000


CMD ["npm", "run", "dev"]
