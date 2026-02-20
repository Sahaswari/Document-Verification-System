FROM node:18-alpine

# Install Python and build tools
RUN apk add --no-cache python3 make g++ netcat-openbsd bash

WORKDIR /app

COPY package*.json ./
RUN npm install

# Copy smart contracts and scripts
COPY . .

# Compile contracts
RUN npx hardhat compile

# Make start script executable
RUN chmod +x /app/start.sh

EXPOSE 8545

CMD ["/bin/sh", "/app/start.sh"]