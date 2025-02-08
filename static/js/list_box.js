document.addEventListener('DOMContentLoaded', async function() {
    try {
        const menuData = await fetchMenuItems('http://127.0.0.1:8000/items/');
        const menuTree = buildMenuTree(menuData);
        const menuHtml = generateMenuHtml(menuTree);
        document.getElementById('sidebar-menu').innerHTML = menuHtml;
    } catch (error) {
        console.error('Error fetching menu items:', error);
    }
});

async function fetchMenuItems(url) {
    const response = await fetch(url);
    if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
    }
    return response.json();
}

function buildMenuTree(items, parentId = null) {
    return items
        .filter(item => (parentId === null ? item.level === 1 : item.parent_id === parentId))
        .map(item => ({
            ...item,
            children: buildMenuTree(items, item.id)
        }));
}

function generateMenuHtml(menuItems) {
    let html = '<ul>';
    for (const item of menuItems) {
        html += `<li class="menu-item"><a href="${item.target_url}">${item.name}</a>`;
        if (item.children && item.children.length) {
            html += generateMenuHtml(item.children); // 递归调用
        }
        html += '</li>';
    }
    html += '</ul>';
    return html;
}