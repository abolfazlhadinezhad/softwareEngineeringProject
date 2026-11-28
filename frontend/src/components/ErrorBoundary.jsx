import { Component } from 'react';

export default class ErrorBoundary extends Component {
  state = { failed: false };
  static getDerivedStateFromError() { return { failed: true }; }
  render() {
    if (this.state.failed) return <main className="state" role="alert"><h1>نمایش صفحه با مشکل روبه‌رو شد</h1><p>صفحه را دوباره بارگذاری کنید. اگر مشکل ادامه داشت، به پشتیبانی اطلاع دهید.</p><button onClick={() => window.location.reload()}>بارگذاری مجدد</button><p><a href="/">بازگشت به خانه</a></p></main>;
    return this.props.children;
  }
}
