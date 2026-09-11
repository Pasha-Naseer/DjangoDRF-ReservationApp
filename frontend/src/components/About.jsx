// Replaces about(). This was just render(request, 'hotel/about.html', {}) with
// no context — so unlike the other pages, there's nothing to fetch. Put
// whatever static copy/markup your old about.html had directly here.
export default function About() {
  return (
    <div>
      <h1>درباره ما</h1>
      <p>{/* paste the content of your old hotel/about.html here */}</p>
    </div>
  );
}
