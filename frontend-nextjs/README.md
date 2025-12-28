# Deep Research Agent - Next.js Frontend

Modern, animated frontend for the Deep Research Agent built with Next.js, React, TypeScript, shadcn/ui, and Framer Motion.

## Features

- 🎨 **Modern UI** - Built with shadcn/ui components and Tailwind CSS
- ✨ **Smooth Animations** - Powered by Framer Motion
- 🔄 **Real-time Updates** - WebSocket integration for live research progress
- 📱 **Responsive Design** - Works seamlessly on desktop and mobile
- 🌙 **Dark Mode Support** - Built-in dark mode styling
- 🎯 **Better UX** - Intuitive interface with progress tracking and live discoveries

## Prerequisites

- Node.js 18+ and npm/yarn/pnpm
- Backend API running on `http://localhost:8000`

## Installation

1. Navigate to the frontend directory:
```bash
cd frontend-nextjs
```

2. Install dependencies:
```bash
npm install
# or
yarn install
# or
pnpm install
```

3. Create a `.env.local` file (optional, defaults are set):
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=localhost:8000
```

## Running the Development Server

```bash
npm run dev
# or
yarn dev
# or
pnpm dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

## Building for Production

```bash
npm run build
npm start
```

## Project Structure

```
frontend-nextjs/
├── app/                    # Next.js app directory
│   ├── layout.tsx         # Root layout
│   ├── page.tsx           # Main page
│   └── globals.css        # Global styles
├── components/
│   ├── ui/                # shadcn/ui components
│   └── research/          # Research-specific components
│       ├── config-panel.tsx
│       ├── progress-tracker.tsx
│       ├── discoveries-feed.tsx
│       └── results-display.tsx
├── lib/
│   ├── api.ts             # API client with WebSocket
│   └── utils.ts           # Utility functions
├── types/
│   └── research.ts        # TypeScript types
└── package.json
```

## Technology Stack

- **Next.js 14** - React framework with App Router
- **React 18** - UI library
- **TypeScript** - Type safety
- **Tailwind CSS** - Utility-first CSS
- **shadcn/ui** - High-quality component library
- **Framer Motion** - Animation library
- **React Markdown** - Markdown rendering
- **Lucide React** - Icon library

## Features Overview

### Configuration Panel
- Clean, modern form with advanced options
- Animated collapsible sections
- Real-time validation

### Progress Tracker
- Visual stage indicators
- Animated progress updates
- Status badges with icons

### Discoveries Feed
- Live updates during research
- Categorized discoveries
- Smooth animations

### Results Display
- Tabbed interface for different views
- Markdown rendering for reports
- Export functionality (Markdown/JSON)
- Refinement capabilities

## Customization

The UI uses Tailwind CSS and shadcn/ui, making it easy to customize:

1. Edit `app/globals.css` for global styles
2. Modify component files in `components/` for specific changes
3. Update `tailwind.config.ts` for theme customization

## Notes

- The frontend connects directly to the backend API (no proxy needed for WebSocket)
- Ensure CORS is configured on the backend to allow `http://localhost:3000`
- WebSocket connections use the `ws://` protocol in development
