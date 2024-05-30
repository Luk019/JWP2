document.addEventListener('DOMContentLoaded', () => {
    const form = document.querySelector('form');
    const taskList = document.getElementById('task-list');

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        const formData = new FormData(form);
        const response = await fetch('/add', {
            method: 'POST',
            body: formData
        });
        if (response.ok) {
            const newTask = await response.json();
            addTaskToList(newTask);
            form.reset();
        }
    });

    taskList.addEventListener('click', async (e) => {
        if (e.target.classList.contains('delete-btn')) {
            const taskId = e.target.dataset.id;
            const response = await fetch(`/delete/${taskId}`, {
                method: 'POST'
            });
            if (response.ok) {
                e.target.closest('li').remove();
            }
        }

        if (e.target.classList.contains('edit-btn')) {
            const taskId = e.target.dataset.id;
            const input = e.target.closest('li').querySelector('.task-content');
            const newContent = input.value;
            const response = await fetch(`/update/${taskId}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ content: newContent })
            });
            if (response.ok) {
                alert('Task updated successfully');
            }
        }
    });

    function addTaskToList(task) {
        const li = document.createElement('li');
        li.innerHTML = `
            <input type="text" class="task-content" value="${task.content}">
            <button class="edit-btn" data-id="${task.id}">Edit</button>
            <button class="delete-btn" data-id="${task.id}">Delete</button>
        `;
        taskList.appendChild(li);
    }
});
