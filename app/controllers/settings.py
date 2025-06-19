from flask import Flask, render_template, abort, request, redirect, flash, url_for
from flask_login import login_required

from app.extensions import db
from app.models.play_option import PlayOptionModel


class SettingsController:
    def __init__(self, app: Flask, play_parameters: dict) -> None:
        self.app = app
        self.play_parameters = play_parameters
        self.register_routes()

    def register_routes(self) -> None:
        self.app.add_url_rule(rule='/settings', view_func=self.settings)
        self.app.add_url_rule(
            rule='/settings/option/add/<param>',
            view_func=self.add_play_option,
            methods=['POST']
        )
        self.app.add_url_rule(
            rule='/settings/option/<int:option_id>/toggle',
            view_func=self.toggle_play_option,
            methods=['POST']
        )
        self.app.add_url_rule(
            rule='/settings/option/<int:option_id>/delete',
            view_func=self.delete_play_option,
            methods=['POST']
        )

    @login_required
    def settings(self):
        options = {}
        for param in self.play_parameters:
            options[param] = PlayOptionModel.query.filter_by(parameter_name=param).all()
        return render_template(
            template_name_or_list='settings/settings.html',
            options=options,
            parameters=self.play_parameters
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
