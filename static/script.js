function fetchData() {
    fetch(`/api/list`)
        .then(res => res.json())
        .then(data => {
            const table = document.getElementById('prTable');
            const thead = table.querySelector('thead');
            const tbody = table.querySelector('tbody');
            thead.innerHTML = '';
            tbody.innerHTML = '';

            if (data.length === 0) return;

            const headers = Object.keys(data[0]);
            const headRow = document.createElement('tr');
            headers.forEach(header => {
                const th = document.createElement('th');
                th.innerText = header;
                headRow.appendChild(th);
            });
            const thDel = document.createElement('th');
            thDel.innerText = "Action";
            headRow.appendChild(thDel);
            thead.appendChild(headRow);

            data.forEach(row => {
                const tr = document.createElement('tr');
                headers.forEach(header => {
                    const td = document.createElement('td');
                    td.innerText = row[header];
                    tr.appendChild(td);
                });
                const tdDel = document.createElement('td');
                const btn = document.createElement('button');
                btn.innerText = "Delete";
                btn.style.color = 'white';
                btn.style.backgroundColor = 'red';
                btn.style.border = 'none';
                btn.style.padding = '4px 8px';
                btn.style.borderRadius = '5px';
                btn.onclick = () => deleteEntry(row["pr_no"]);
                tdDel.appendChild(btn);
                tr.appendChild(tdDel);
                tbody.appendChild(tr);
            });
        });
}

function deleteEntry(prNo) {
    fetch('/api/delete', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ pr_no: prNo })
    }).then(() => fetchData());
}

document.getElementById('prForm').addEventListener('submit', function (e) {
    e.preventDefault();
    const formData = new FormData(this);
    const jsonData = Object.fromEntries(formData.entries());

    fetch('/api/add', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(jsonData)
    }).then(() => {
        this.reset();
        fetchData();
    });
});

fetchData();
