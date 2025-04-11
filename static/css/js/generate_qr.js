function generateQR(canvasId, relativeUrl) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) return;

    const fullUrl = window.location.origin + relativeUrl;

    new QRious({
        element: canvas,
        value: fullUrl,
        size: 140
    });
}
