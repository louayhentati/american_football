document.addEventListener('DOMContentLoaded', () => {
    const teamCard = document.querySelector('#btnEditTeam')?.closest('.card');
    const playCallCard = document.querySelector('#btnEditPlayCall')?.closest('.card');

    const btnEditTeam = document.getElementById('btnEditTeam');
    const btnCancelTeam = document.getElementById('btnCancelTeam');
    const teamDisplay = document.getElementById('teamDisplay');
    const teamForm = document.getElementById('teamForm');

    if (btnEditTeam) {
        btnEditTeam.addEventListener('click', () => {
            teamDisplay.style.display = 'none';
            btnEditTeam.style.display = 'none';
            teamForm.style.display = 'block';
            if (teamCard) teamCard.classList.remove('card-collapsed');
        });
    }

    if (btnCancelTeam) {
        btnCancelTeam.addEventListener('click', () => {
            teamForm.style.display = 'none';
            teamDisplay.style.display = 'flex';
            btnEditTeam.style.display = 'inline-block';
            if (teamCard) teamCard.classList.add('card-collapsed');
        });
    }

    const btnEditPlayCall = document.getElementById('btnEditPlayCall');
    const btnCancelPlayCall = document.getElementById('btnCancelPlayCall');
    const displayPlayCall = document.getElementById('defaultPlayCallDisplay');
    const formPlayCall = document.getElementById('defaultPlayCallForm');

    if (btnEditPlayCall) {
        btnEditPlayCall.addEventListener('click', () => {
            displayPlayCall.style.display = 'none';
            btnEditPlayCall.style.display = 'none';
            formPlayCall.style.display = 'block';
            if (playCallCard) playCallCard.classList.remove('card-collapsed');
        });
    }

    if (btnCancelPlayCall) {
        btnCancelPlayCall.addEventListener('click', () => {
            formPlayCall.style.display = 'none';
            displayPlayCall.style.display = 'flex';
            btnEditPlayCall.style.display = 'inline-block';
            if (playCallCard) playCallCard.classList.add('card-collapsed');
        });
    }
});