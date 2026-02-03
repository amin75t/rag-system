# IRANSansX Font Integration

This project has been integrated with the IRANSansX font family, which provides excellent support for Persian (Farsi) text rendering.

## Font Files

All IRANSansX font files are located in `src/assets/font/`:
- IRANSansX-Thin.woff2 (Weight: 100)
- IRANSansX-UltraLight.woff2 (Weight: 200)
- IRANSansX-Light.woff2 (Weight: 300)
- IRANSansX-Regular.woff2 (Weight: 400)
- IRANSansX-Medium.woff2 (Weight: 500)
- IRANSansX-DemiBold.woff2 (Weight: 600)
- IRANSansX-Bold.woff2 (Weight: 700)
- IRANSansX-ExtraBold.woff2 (Weight: 800)
- IRANSansX-Black.woff2 (Weight: 900)

## Usage in Components

### Using Tailwind CSS Classes

```jsx
// Apply the font family to an element
<div className="font-iransans">متن فارسی</div>

// Apply specific font weights
<div className="font-iransans font-thin">متن نازک</div>
<div className="font-iransans font-bold">متن ضخیم</div>
```

### Using Custom Font Weight Classes

```jsx
// Use the specific IRANSansX weight classes
<div className="font-iransans-regular">متن عادی</div>
<div className="font-iransans-medium">متن متوسط</div>
<div className="font-iransans-bold">متن ضخیم</div>
```

### Using Inline Styles

```jsx
<div style={{ fontFamily: 'IRANSansX, sans-serif' }}>
  متن فارسی با فونت IRANSansX
</div>
```

## Global Application

The font is applied globally to the body element in `src/styles/fonts.css`, so all text will use IRANSansX by default.

## Configuration

- Font face definitions are in `src/styles/fonts.css`
- Tailwind configuration is in `tailwind.config.js`
- Font files are properly handled in `vite.config.ts`

## RTL Support

The project already includes RTL (Right-to-Left) support for Persian text. Make sure to include `dir="rtl"` in your HTML elements or use the Tailwind RTL utilities.