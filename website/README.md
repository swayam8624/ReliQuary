# ReliQuary Website

Professional marketing website for ReliQuary's enterprise-grade cryptographic memory platform.

## 🚀 Features

- **Modern Tech Stack**: Next.js 14, React 18, TypeScript, Tailwind CSS
- **Responsive Design**: Mobile-first approach with beautiful animations
- **Performance Optimized**: Lightning-fast loading with Vercel optimization
- **SEO Optimized**: Complete meta tags, structured data, and social sharing
- **Accessible**: WCAG 2.1 AA compliant with semantic HTML
- **Interactive**: Smooth animations and micro-interactions

## 📁 Project Structure

```
website/
├── src/
│   ├── app/                    # Next.js 13+ app directory
│   │   ├── layout.tsx          # Root layout with metadata
│   │   └── page.tsx            # Landing page
│   ├── components/             # React components
│   │   ├── Header.tsx          # Navigation header
│   │   ├── Hero.tsx            # Hero section
│   │   ├── Features.tsx        # Features showcase
│   │   ├── Pricing.tsx         # Pricing tiers
│   │   ├── Testimonials.tsx    # Customer testimonials
│   │   ├── CTA.tsx             # Call-to-action
│   │   ├── Footer.tsx          # Site footer
│   │   └── SocialIcons.tsx     # Social media icons
│   └── styles/
│       └── globals.css         # Global styles and Tailwind
├── public/                     # Static assets
├── package.json                # Dependencies and scripts
├── next.config.js              # Next.js configuration
├── tailwind.config.js          # Tailwind CSS configuration
├── tsconfig.json               # TypeScript configuration
└── README.md                   # This file
```

## 🛠 Getting Started

### Prerequisites

- Node.js 18+
- npm or yarn

### Installation

1. **Install dependencies:**

   ```bash
   cd website
   npm install
   ```

2. **Run development server:**

   ```bash
   npm run dev
   ```

3. **Open your browser:**
   Navigate to `http://localhost:3000`

### Build for Production

```bash
# Build the application
npm run build

# Start production server
npm start

# Export static files (optional)
npm run export
```

## 🎨 Design System

### Colors

- **Primary**: Blue gradient (#0ea5e9 to #0369a1)
- **Secondary**: Gray scale (#f8fafc to #0f172a)
- **Accent**: Pink/Purple (#ec4899)
- **Success**: Green (#22c55e)
- **Warning**: Orange (#f59e0b)
- **Error**: Red (#ef4444)

### Typography

- **Font Family**: Inter (Google Fonts)
- **Monospace**: JetBrains Mono
- **Display**: Cal Sans (for headings)

### Components

- **Buttons**: Primary, secondary, and outline variants
- **Cards**: Glassmorphism and solid styles
- **Forms**: Consistent input styling with focus states
- **Navigation**: Responsive with smooth transitions

## 📱 Responsive Breakpoints

- **sm**: 640px
- **md**: 768px
- **lg**: 1024px
- **xl**: 1280px
- **2xl**: 1536px

## ⚡ Performance Features

- **Image Optimization**: Next.js automatic image optimization
- **Code Splitting**: Automatic code splitting by Next.js
- **Lazy Loading**: Components and images load on demand
- **Caching**: Aggressive caching strategies
- **Compression**: Gzip and Brotli compression

## 🔍 SEO Features

- **Meta Tags**: Complete Open Graph and Twitter Card support
- **Structured Data**: JSON-LD for rich snippets
- **Sitemap**: Automatic sitemap generation
- **Canonical URLs**: Proper canonical URL handling
- **Performance**: 95+ Lighthouse scores

## 🎭 Animation Libraries

- **Framer Motion**: Page transitions and component animations
- **Tailwind Animations**: CSS-based animations for performance
- **Intersection Observer**: Scroll-triggered animations

## 📊 Analytics & Tracking

- **Google Analytics**: User behavior tracking
- **Hotjar**: Heatmaps and user session recordings
- **Performance Monitoring**: Core Web Vitals tracking

## 🚀 Deployment

### Vercel (Recommended)

1. **Connect repository to Vercel**
2. **Configure environment variables**
3. **Deploy automatically on push**

### Manual Deployment

```bash
# Build the application
npm run build

# Deploy the .next folder to your hosting provider
```

### Environment Variables

```env
# Analytics
NEXT_PUBLIC_GA_ID=UA-XXXXXXXXX-X
NEXT_PUBLIC_HOTJAR_ID=XXXXXXX

# API URLs
NEXT_PUBLIC_API_URL=https://api.reliquary.io
NEXT_PUBLIC_DOCS_URL=https://docs.reliquary.io

# Feature Flags
NEXT_PUBLIC_ENABLE_CHAT=true
NEXT_PUBLIC_ENABLE_DEMOS=true
```

## 🧪 Testing

```bash
# Run ESLint
npm run lint

# Run type checking
npx tsc --noEmit

# Run Lighthouse audit
npm run audit
```

## 📈 Performance Benchmarks

- **Lighthouse Performance**: 95+
- **First Contentful Paint**: < 1.5s
- **Largest Contentful Paint**: < 2.5s
- **Cumulative Layout Shift**: < 0.1
- **Time to Interactive**: < 3.5s

## 🌐 Browser Support

- **Chrome**: 90+
- **Firefox**: 88+
- **Safari**: 14+
- **Edge**: 90+

## 📝 Content Management

### Adding New Sections

1. Create component in `src/components/`
2. Import and add to `src/app/page.tsx`
3. Update navigation in `Header.tsx` if needed

### Updating Content

- **Pricing**: Edit `src/components/Pricing.tsx`
- **Features**: Edit `src/components/Features.tsx`
- **Testimonials**: Edit `src/components/Testimonials.tsx`

### Adding Blog Posts

```bash
# Create new blog post
mkdir src/app/blog/[slug]
touch src/app/blog/[slug]/page.tsx
```

## 🔧 Customization

### Theme Colors

Edit `tailwind.config.js` to customize the color palette:

```js
module.exports = {
  theme: {
    extend: {
      colors: {
        primary: {
          // Your custom colors
        },
      },
    },
  },
};
```

### Fonts

Update `src/app/layout.tsx` to change fonts:

```tsx
import { YourFont } from "next/font/google";

const yourFont = YourFont({ subsets: ["latin"] });
```

## 📚 Additional Resources

- [Next.js Documentation](https://nextjs.org/docs)
- [Tailwind CSS Documentation](https://tailwindcss.com/docs)
- [Framer Motion Documentation](https://www.framer.com/motion/)
- [Vercel Deployment Guide](https://vercel.com/docs)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details

---

**Built with ❤️ by the ReliQuary Team**
