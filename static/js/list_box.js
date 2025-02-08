document.addEventListener('DOMContentLoaded', async function() {
    try {
        // 1. 从后端获取菜单数据
        const menuData = await fetchMenuItems('http://127.0.0.1:8000/items/');
        const menuTree = buildMenuTree(menuData);
        const menuHtml = generateMenuHtml(menuTree);

        // 2. 将生成的HTML设置到侧边栏容器
        document.getElementById('sidebar-menu').innerHTML = menuHtml;

        // 3. 初始化侧边栏宽度调整功能
        initResizeHandle();

        // 4. 初始化菜单展开/折叠功能
        initMenuToggle();
    } catch (error) {
        console.error('Error fetching menu items:', error);
    }
});

async function fetchMenuItems(url) {
    const response = await fetch(url);
    if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
    }
    return await response.json();
}

function buildMenuTree(items, parentHierarchy = null) {
    return items
        .filter(item => {
            // Match top-level items if no parentHierarchy, else match children of the given parent
            return parentHierarchy === null ? item.hierarchy_code.match(/^\d+-0-0$/) : item.hierarchy_code.startsWith(parentHierarchy) && item.hierarchy_code !== parentHierarchy;
        })
        .map(item => ({
            ...item,
            children: buildMenuTree(items, getNextLevelHierarchy(item.hierarchy_code))
        }));
}

function getNextLevelHierarchy(hierarchy_code) {
    let parts = hierarchy_code.split('-').map(Number);
    if (parts[2] === 0) { // It's a top-level or second-level item
        parts[1] += 1;
    } else { // It's a third-level or deeper item
        parts[2] += 1;
    }
    return parts.join('-').replace(/-0$/, ''); // Remove trailing -0 for parent matching
}

function generateMenuHtml(menuItems) {
    let html = '<ul class="menu-list">';
    for (const item of menuItems) {
        const hasChildren = item.children && item.children.length;
        html += `<li class="menu-item${hasChildren ? ' has-children' : ''}">`;
        html += `<span class="menu-toggle">${item.name}</span>`;
        if (hasChildren) {
            html += `<div class="sub-menu">${generateMenuHtml(item.children)}</div>`; // 递归调用
        }
        html += '</li>';
    }
    html += '</ul>';
    return html;
}


// 初始化侧边栏宽度调整功能
function initResizeHandle() {
    const sidebar = document.getElementById('sidebar-menu');
    const handle = document.createElement('div');
    handle.className = 'resize-handle';
    sidebar.appendChild(handle);

    let isResizing = false;
    let lastX = 0;

    handle.addEventListener('mousedown', function(e) {
        isResizing = true;
        lastX = e.clientX;
        document.addEventListener('mousemove', handleMouseMove);
        document.addEventListener('mouseup', stopResize);
    });

    function handleMouseMove(e) {
        if (!isResizing) return;
        const dx = e.clientX - lastX;
        const newWidth = parseInt(getComputedStyle(sidebar).width, 10) + dx;
        sidebar.style.width = `${newWidth}px`;
        lastX = e.clientX;
    }

    function stopResize() {
        isResizing = false;
        document.removeEventListener('mousemove', handleMouseMove);
        document.removeEventListener('mouseup', stopResize);
    }
}

document.addEventListener('DOMContentLoaded', function() {
    // 添加事件监听到所有的菜单切换元素
    document.querySelectorAll('.menu-toggle').forEach(function(toggle) {
        toggle.addEventListener('click', function() {
            const subMenu = toggle.nextElementSibling;
            if (subMenu && subMenu.classList.contains('sub-menu')) {
                // 切换子菜单的显示状态
                subMenu.style.display = subMenu.style.display === 'block' ? 'none' : 'block';
            }
        });
    });
});

function initMenuToggle() {
    document.querySelectorAll('.menu-toggle').forEach(function(toggle) {
        toggle.addEventListener('click', function() {
            const subMenu = toggle.nextElementSibling;
            if (subMenu && subMenu.classList.contains('sub-menu')) {
                subMenu.style.display = subMenu.style.display === 'block' ? 'none' : 'block';
            }
        });
    });
}