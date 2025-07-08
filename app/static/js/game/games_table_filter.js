window.addEventListener('DOMContentLoaded', function () {
    const table = $('#gamesTable').DataTable({
        dom: 't',
    });

    $('#awayTeamFilter').select2({
        theme: 'bootstrap-5', placeholder: 'Select Away Team', allowClear: true, width: 'resolve'
    });

    $('#awayTeamFilter').on('change', function () {
        const selectedTeam = $(this).val();
        table.column(4).search(selectedTeam || '', false, false).draw();
    });
});