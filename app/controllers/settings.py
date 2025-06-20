from flask import Flask, render_template, abort, request, redirect, flash, url_for
from flask_login import login_required

from app.extensions import db
from app.models.play_option import PlayOptionModel
from app.models.play_call import PlayCallModel


class SettingsController:
    def __init__(self, app: Flask, play_parameters: dict) -> None:
        self.app = app
        self.play_parameters = play_parameters
        self.register_routes()

    def register_routes(self) -> None:
        self.app.add_url_rule(
            rule='/settings',
            view_func=self.settings)
        self.app.add_url_rule(
            rule='/settings/play/option/add/<param>',
            view_func=self.add_play_option,
            methods=['POST']
        )

        self.app.add_url_rule(
            rule='/settings/play/option/<int:option_id>/toggle',
            view_func=self.toggle_play_option,
            methods=['POST']
        )

        self.app.add_url_rule(
            rule='/settings/play/option/<int:option_id>/delete',
            view_func=self.delete_play_option,
            methods=['POST']
        )

        self.app.add_url_rule(
            rule='/settings/play/call/add',
            view_func=self.add_play_call,
            methods=['POST']
        )

        self.app.add_url_rule(
            rule='/settings/play/call/delete/<int:call_id>',
            view_func=self.delete_play_call,
            methods=['POST']
        )

        self.app.add_url_rule(
            rule='/settings/play/call/<int:call_id>/toggle',
            view_func=self.toggle_play_call,
            methods=['POST']
        )

    @login_required
    def settings(self):
        options = {}
        calls = self.__load_play_calls()
        for param in self.play_parameters:
            options[param] = PlayOptionModel.query.filter_by(parameter_name=param).all()
        return render_template(
            template_name_or_list='settings/settings.html',
            options=options,
            parameters=self.play_parameters,
            play_calls=calls
        )

    @login_required
    def add_play_option(self, param):
        if param not in self.play_parameters:
            abort(code=404)
        value = request.form.get('value')
        option = PlayOptionModel(parameter_name=param, value=value)
        db.session.add(option)
        db.session.commit()
        flash(f'Added option "{value}" to {self.play_parameters[param]}')
        return redirect(url_for('settings'))

    @login_required
    def toggle_play_option(self, option_id):
        option = PlayOptionModel.query.get_or_404(option_id)
        option.enabled = not option.enabled
        db.session.commit()
        return redirect(url_for('settings'))

    @login_required
    def delete_play_option(self, option_id):
        option = PlayOptionModel.query.get_or_404(option_id)
        db.session.delete(option)
        db.session.commit()
        return redirect(url_for('settings'))

    @login_required
    def add_play_call(self):
        name = request.form.get('name')

        if not name:
            flash('Play Call name is required.', 'danger')
            return redirect(url_for('settings'))

        existing = PlayCallModel.query.filter(db.func.lower(PlayCallModel.name) == name.lower()).first()
        if existing:
            flash(f'Play Call "{name}" already exists.', 'warning')
            return redirect(url_for('settings'))

        new_call = PlayCallModel(name=name.strip(), status=True)
        db.session.add(new_call)
        db.session.commit()

        flash(f'Play Call "{name}" added successfully.', 'success')
        return redirect(url_for('settings'))

    @login_required
    def delete_play_call(self, call_id):
        call = PlayCallModel.query.get_or_404(call_id)
        db.session.delete(call)
        db.session.commit()
        flash(f'Play Call "{call.name}" deleted successfully.', 'success')
        return redirect(url_for('settings'))

    @login_required
    def toggle_play_call(self, call_id):
        call = PlayCallModel.query.get_or_404(call_id)
        call.status = not call.status
        db.session.commit()

        state = "enabled" if call.status else "disabled"
        flash(f'Play Call "{call.name}" {state}.', 'success')
        return redirect(url_for('settings'))

    @staticmethod
    def __load_play_calls():
        return [{'id': call.id, 'name': call.name, 'status': call.status} for call in PlayCallModel.query.all()]
