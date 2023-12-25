export async function GET() {
    const recaptcha_site_key = process.env.VITE_RECAPTCHA_SITE_KEY; // Replace with your actual env variable
  
    return new Response(JSON.stringify({ variable: recaptcha_site_key }), {
      headers: {
        'Content-Type': 'application/json'
      }
    });
  }