
document.addEventListener("DOMContentLoaded", () => {
    const container = document.getElementById("tool-explorer");
    if (!container) return;
    
    // Create UI
    const searchInput = document.createElement("input");
    searchInput.type = "text";
    searchInput.placeholder = "Search tools by name or description...";
    searchInput.style.width = "100%";
    searchInput.style.padding = "8px";
    searchInput.style.marginBottom = "16px";
    
    const listContainer = document.createElement("div");
    
    container.appendChild(searchInput);
    container.appendChild(listContainer);
    
    let allTools = [];
    
    function renderTree(obj) {
        if (!obj || typeof obj !== "object") return String(obj);
        const ul = document.createElement("ul");
        for (const [key, value] of Object.entries(obj)) {
            const li = document.createElement("li");
            if (typeof value === "object" && value !== null) {
                const details = document.createElement("details");
                const summary = document.createElement("summary");
                summary.innerHTML = "<strong>" + key + "</strong>";
                details.appendChild(summary);
                details.appendChild(renderTree(value));
                li.appendChild(details);
            } else {
                li.innerHTML = "<strong>" + key + ":</strong> " + value;
            }
            ul.appendChild(li);
        }
        return ul;
    }
    
    function renderTools(tools) {
        listContainer.innerHTML = "";
        tools.forEach(t => {
            const card = document.createElement("div");
            card.style.border = "1px solid #ccc";
            card.style.padding = "16px";
            card.style.marginBottom = "16px";
            card.style.borderRadius = "4px";
            
            const title = document.createElement("h3");
            title.textContent = t.name;
            title.style.marginTop = "0";
            
            const desc = document.createElement("p");
            desc.textContent = t.description;
            
            const schemaTitle = document.createElement("h4");
            schemaTitle.textContent = "Input Schema";
            
            card.appendChild(title);
            card.appendChild(desc);
            card.appendChild(schemaTitle);
            card.appendChild(renderTree(t.inputSchema));
            
            listContainer.appendChild(card);
        });
    }
    
    // Determine path prefix based on the script location to support multi-level static folders
    const currentScript = document.currentScript || document.querySelector('script[src*="explorer.js"]');
    let basePath = "./";
    if (currentScript) {
        const src = currentScript.getAttribute("src");
        const index = src.indexOf("js/explorer.js");
        if (index !== -1) {
            basePath = src.substring(0, index);
        }
    }
    
    fetch(`${basePath}js/tools_catalog.json`)
        .then(res => {
            if (!res.ok) {
                throw new Error(`HTTP error! status: ${res.status}`);
            }
            return res.json();
        })
        .then(data => {
            allTools = data;
            renderTools(allTools);
        })
        .catch(e => {
            console.error("Failed to load catalog", e);
            listContainer.innerHTML = "<p>Failed to load tool schemas.</p>";
        });
    
    searchInput.addEventListener("input", (e) => {
        const query = e.target.value.toLowerCase();
        const filtered = allTools.filter(t => 
            t.name.toLowerCase().includes(query) || 
            t.description.toLowerCase().includes(query)
        );
        renderTools(filtered);
    });
});
