def test_cli_run_cli_is_exposed_from_session():
    assert callable(cli.run_cli)


def test_main_delegates_to_cli_run_cli(monkeypatch):
    called = {"run_cli": 0}

    monkeypatch.setattr(main, "run_cli", lambda: called.__setitem__("run_cli", called["run_cli"] + 1))

    main.main()

    assert called["run_cli"] == 1
