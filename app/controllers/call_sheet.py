from flask import Flask, render_template
from flask_login import login_required
from app.models.drive import DriveModel
from app.models.play import PlayModel


class CallSheetController:
    def __init__(self, app: Flask) -> None:
        self.app = app
        self.register_routes()

    def register_routes(self) -> None:
        self.app.add_url_rule(rule='/callsheet', view_func=self.callsheet)
        self.app.add_url_rule(rule='/game/<int:game_id>/game_callsheet', view_func=self.game_callsheet)

    @login_required
    def callsheet(self) -> str:
        plays = PlayModel.query.filter(PlayModel.odk == 'O').all()
        callsheet_entries = self._process_plays(plays)
        return render_template(template_name_or_list='play/callsheet.html', callsheet_entries=callsheet_entries)

    @login_required
    def game_callsheet(self, game_id: int) -> str:
        plays = PlayModel.query.join(DriveModel).filter(
            DriveModel.game_id == game_id,
            PlayModel.odk == 'O'
        ).all()
        callsheet_entries = self._process_plays(plays)
        return render_template(
            template_name_or_list='game/game_callsheet.html',
            callsheet_entries=callsheet_entries,
            game_id=game_id
        )

    @staticmethod
    def _process_plays(plays: list) -> list:
        callsheet_data = {}

        for play in plays:
            key = (play.off_play, play.off_form, play.form_adj)

            if key not in callsheet_data:
                callsheet_data[key] = {'count': 0, 'total_gain_loss': 0}

            callsheet_data[key]['count'] += 1
            callsheet_data[key]['total_gain_loss'] += play.gain_loss

        total_plays = sum(data['count'] for data in callsheet_data.values())
        entries = []

        for key, data in callsheet_data.items():
            off_play, off_form, form_adj = key
            count = data['count']
            total = data['total_gain_loss']
            percent = (count / total_plays) * 100 if total_plays > 0 else 0
            average = total / count if count > 0 else 0

            entries.append({
                'off_play': off_play,
                'off_form': off_form,
                'form_adj': form_adj,
                'count': count,
                'percent': percent,
                'total': total,
                'average': average,
            })

        return sorted(entries, key=lambda x: x['count'], reverse=True)
