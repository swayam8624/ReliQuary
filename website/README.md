# ReliQuary - Enterprise-Grade Cryptographic Memory Platform

![How Vulnerable Are You?](../How%20Vulnerable%20Are%20You_.gif)

**The World's First Post-Quantum Memory Vault**

Secure your digital assets against today's threats and tomorrow's quantum computers. Built with military-grade cryptography, zero-knowledge proofs, and intelligent multi-agent consensus for unparalleled protection.

[![Vercel Deployment](https://vercelbadge.vercel.app/api/reliquary/website)](https://reliquary-kairoki.vercel.app)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Next.js](https://img.shields.io/badge/Next.js-14-black)](https://nextjs.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5-blue)](https://www.typescriptlang.org/)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind%20CSS-3-blue)](https://tailwindcss.com/)

## 🌐 Our Website

**Visit our live website:** [https://reliquary-kairoki.vercel.app](https://reliquary-kairoki.vercel.app)

## 🚀 Features

### 🔒 Post-Quantum Security

- **PQC Algorithms**: Lattice-based cryptography resistant to quantum attacks
- **Hybrid Encryption**: Combines classical and post-quantum algorithms for maximum security
- **Key Rotation**: Automatic key rotation with zero-downtime transitions

### 🧠 Intelligent Multi-Agent Consensus

- **Distributed Verification**: Multi-agent system validates all transactions
- **Adaptive Consensus**: Adjusts consensus mechanism based on network conditions
- **Fault Tolerance**: Byzantine Fault Tolerance with 99.99% uptime guarantee

### 🕵️ Zero-Knowledge Proofs

- **Privacy-Preserving**: Verify without revealing sensitive information
- **Efficient Proving**: Constant-time proof generation and verification
- **Selective Disclosure**: Choose what information to reveal in each context

### 📊 Performance Metrics

| Metric                 | Score  | Industry Benchmark |
| ---------------------- | ------ | ------------------ |
| Security Rating        | A+     | A                  |
| Load Time              | < 1.2s | < 3s               |
| Lighthouse Performance | 98/100 | 90+                |
| Mobile Score           | 95/100 | 85+                |
| Accessibility          | 92/100 | 80+                |

## 🛠 Getting Started

### Prerequisites

- Node.js 18+
- npm or yarn
- Git

### Installation

1. **Clone the repository:**

   ```bash
   git clone https://github.com/reliquary/reliquary-platform.git
   cd reliquary-platform/website
   ```

2. **Install dependencies:**

   ```bash
   npm install
   # or
   yarn install
   ```

3. **Run development server:**

   ```bash
   npm run dev
   # or
   yarn dev
   ```

4. **Open your browser:**
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
│   │   └── Footer.tsx          # Site footer
│   └── styles/
│       └── globals.css         # Global styles and Tailwind
├── public/                     # Static assets
├── package.json                # Dependencies and scripts
├── next.config.js              # Next.js configuration
├── tailwind.config.js          # Tailwind CSS configuration
└── README.md                   # This file
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
- **Headings**: Cal Sans (for display headings)
- **Monospace**: JetBrains Mono

### Components

- **Buttons**: Primary, secondary, and outline variants
- **Cards**: Glassmorphism and solid styles
- **Forms**: Consistent input styling with focus states
- **Navigation**: Responsive with smooth transitions

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

## 📱 Responsive Breakpoints

- **sm**: 640px
- **md**: 768px
- **lg**: 1024px
- **xl**: 1280px
- **2xl**: 1536px

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

## 🐳 Docker Deployment

ReliQuary provides official Docker images for easy deployment across multiple environments. Our images are built for multiple architectures (AMD64, ARM64, ARMv7) and are available on Docker Hub.

### Official Docker Images

| Image                                                                                                           | Tag    | Description                |
| --------------------------------------------------------------------------------------------------------------- | ------ | -------------------------- |
| [swayamsingal/reliquary-platform](https://hub.docker.com/r/swayamsingal/reliquary-platform)                     | v5.0.0 | Main ReliQuary platform    |
| [swayamsingal/reliquary-agent-orchestrator](https://hub.docker.com/r/swayamsingal/reliquary-agent-orchestrator) | v5.0.0 | Agent orchestrator service |
| [swayamsingal/reliquary-website](https://hub.docker.com/r/swayamsingal/reliquary-website)                       | v1.0.0 | Marketing website          |

### Pull and Run Docker Images

```bash
# Pull the platform image
docker pull swayamsingal/reliquary-platform:v5.0.0

# Run the platform container
docker run -d \
  --name reliquary-platform \
  -p 8080:8080 \
  -e RELIQUARY_ENV=production \
  swayamsingal/reliquary-platform:v5.0.0

# Pull the website image
docker pull swayamsingal/reliquary-website:v1.0.0

# Run the website container
docker run -d \
  --name reliquary-website \
  -p 3000:3000 \
  swayamsingal/reliquary-website:v1.0.0
```

### Docker Compose Setup

For a complete development environment, use our Docker Compose configuration:

```bash
# Clone the repository
git clone https://github.com/reliquary/reliquary-platform.git
cd reliquary-platform

# Start all services
docker-compose up -d

# Start production services
docker-compose -f docker/docker-compose.prod.yml up -d
```

### Building from Source

To build Docker images from source:

```bash
# Build platform image
docker build -t reliquary/platform:v5.0.0 -f Dockerfile.platform --target production .

# Build orchestrator image
docker build -t reliquary/agent-orchestrator:v5.0.0 -f Dockerfile.agent-orchestrator .

# Build website image
docker build -t reliquary/website:v1.0.0 -f website/Dockerfile .
```

### Multi-Architecture Support

Our Docker images support multiple architectures:

- AMD64 (x86_64)
- ARM64 (aarch64)
- ARMv7 (armhf)

To build for specific architectures:

```bash
# Build for ARM64
docker buildx build --platform linux/arm64 -t reliquary/platform:v5.0.0 .

# Build for multiple architectures
docker buildx build --platform linux/amd64,linux/arm64,linux/arm/v7 -t reliquary/platform:v5.0.0 .
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

| Test                     | Score  | Target |
| ------------------------ | ------ | ------ |
| Lighthouse Performance   | 98/100 | >95    |
| First Contentful Paint   | < 1.2s | < 1.5s |
| Largest Contentful Paint | < 2.1s | < 2.5s |
| Cumulative Layout Shift  | 0.01   | < 0.1  |
| Time to Interactive      | < 2.8s | < 3.5s |

## 🌐 Browser Support

| Browser       | Version | Status       |
| ------------- | ------- | ------------ |
| Chrome        | 90+     | ✅ Supported |
| Firefox       | 88+     | ✅ Supported |
| Safari        | 14+     | ✅ Supported |
| Edge          | 90+     | ✅ Supported |
| Mobile Safari | 14+     | ✅ Supported |
| Chrome Mobile | 90+     | ✅ Supported |

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

MIT License - see [LICENSE](LICENSE) file for details

---

**Built with ❤️ by the ReliQuary Team**

_Securing the digital future against quantum threats_
