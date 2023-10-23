const notification = document.getElementById("notification");

fetch("http://localhost:8000/diseases_today")
    .then((response) => response.json())
    .then((data) => {
        data.forEach((entry) => {
            const listItem = document.createElement("div");
            listItem.innerHTML = `
            <li>
                <a href="##">
                    <div class="notification-dropdown-icon info">
                        <svg xmlns="http://www.w3.org/2000/svg" height="1em" viewBox="0 0 512 512"><!--! Font Awesome Free 6.4.2 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license (Commercial License) Copyright 2023 Fonticons, Inc. --><style>svg{fill:#5eca87}</style><path d="M272 96c-78.6 0-145.1 51.5-167.7 122.5c33.6-17 71.5-26.5 111.7-26.5h88c8.8 0 16 7.2 16 16s-7.2 16-16 16H288 216s0 0 0 0c-16.6 0-32.7 1.9-48.2 5.4c-25.9 5.9-50 16.4-71.4 30.7c0 0 0 0 0 0C38.3 298.8 0 364.9 0 440v16c0 13.3 10.7 24 24 24s24-10.7 24-24V440c0-48.7 20.7-92.5 53.8-123.2C121.6 392.3 190.3 448 272 448l1 0c132.1-.7 239-130.9 239-291.4c0-42.6-7.5-83.1-21.1-119.6c-2.6-6.9-12.7-6.6-16.2-.1C455.9 72.1 418.7 96 376 96L272 96z"/></svg>         
                    </div>
                    <div class="notification-dropdown-text">
                        <span class="notification-dropdown__title"> ${entry.disease} </span>
                        <span class="notification-dropdown__subtitle">Read more
                            here.</span>
                    </div>
                </a>
            </li>
        `;
            notification.appendChild(listItem);
        });
    })
    .catch((error) => {
        console.error("Error:", error);
    });