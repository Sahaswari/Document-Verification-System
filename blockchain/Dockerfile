FROM node:18-alpine

# Install Python and build tools
RUN apk add --no-cache python3 make g++ netcat-openbsd

WORKDIR /app

COPY package*.json ./
RUN npm install

# Copy smart contracts and scripts
COPY . .

EXPOSE 8545

CMD ["npx", "hardhat", "node"]