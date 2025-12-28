# Quick Start Guide - Next.js Frontend

## Prerequisites

- Node.js 18+ installed
- Backend API running on `http://localhost:8000` (see main README for backend setup)

## Installation

1. **Navigate to the frontend directory:**
   ```bash
   cd frontend-nextjs
   ```

2. **Install dependencies:**
   ```bash
   npm install
   # or
   yarn install
   # or
   pnpm install
   ```

3. **Start the development server:**
   ```bash
   npm run dev
   ```

4. **Open your browser:**
   Navigate to [http://localhost:3000](http://localhost:3000)

## Features

✨ **Modern UI Components**
- Built with shadcn/ui for beautiful, accessible components
- Tailwind CSS for responsive styling
- Dark mode support

🎨 **Smooth Animations**
- Framer Motion for fluid transitions
- Real-time progress indicators
- Animated discovery feed

🔄 **Real-time Updates**
- WebSocket integration for live progress
- Live discoveries feed
- Progress tracker with stage indicators

📊 **Better UX**
- Tabbed results display
- Markdown rendering for reports
- Export functionality (Markdown/JSON)
- Research refinement capabilities

## Configuration

The frontend connects to the backend API. By default:
- API URL: `http://localhost:8000`
- WebSocket: `ws://localhost:8000/ws/research`

To change these, create a `.env.local` file:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=localhost:8000
```

## Building for Production

```bash
npm run build
npm start
```

## Troubleshooting

**WebSocket connection issues:**
- Ensure the backend is running on port 8000
- Check that CORS is configured to allow `http://localhost:3000`
- Verify the WebSocket URL in `.env.local`

**Build errors:**
- Make sure all dependencies are installed: `npm install`
- Clear `.next` folder and rebuild: `rm -rf .next && npm run build`

**Port already in use:**
- Change the port: `npm run dev -- -p 3001`
