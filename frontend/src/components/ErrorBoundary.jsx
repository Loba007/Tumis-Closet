import { Component } from "react";

export default class ErrorBoundary extends Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError() {
    return { hasError: true };
  }

  componentDidCatch(error, info) {
    console.error("Unexpected UI error", error, info);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="max-w-xl mx-auto px-5 py-28 text-center">
          <p className="label-track text-xs text-gold-dark mb-4">Something went wrong</p>
          <h1 className="font-display text-3xl mb-4">We hit a snag</h1>
          <p className="text-stone text-sm mb-8">
            Please refresh the page. If it keeps happening, message us on WhatsApp and we
            will help you finish your order.
          </p>
          <button onClick={() => window.location.reload()} className="btn btn-primary">
            Refresh page
          </button>
        </div>
      );
    }
    return this.props.children;
  }
}
