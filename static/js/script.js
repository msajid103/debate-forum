<script>
    // Function to generate a random red shade
    function getRandomRedColor() {
        const red = 255; // Maximum red
        const green = Math.floor(Math.random() * 150); // Random green (0-150 for red shades)
        const blue = Math.floor(Math.random() * 150);  // Random blue (0-150 for red shades)
        return `rgb(${red}, ${green}, ${blue})`;
    }

    // Apply random red shades to cards
    document.addEventListener("DOMContentLoaded", () => {
        const cards = document.querySelectorAll('.card');
        cards.forEach(card => {
            card.style.borderTopColor = getRandomRedColor();
        });
    });
</script>
