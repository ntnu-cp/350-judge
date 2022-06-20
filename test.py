from judge import cmp, preprocess_output


def test_preprocess_output():
    assert preprocess_output('a\n\nb\n') == 'a\n\nb'
    assert preprocess_output('a   \nb\n\n') == 'a\nb'


def test_cmp():
    assert cmp('a\n\nb\n', 'a    \n\nb')
    assert not cmp('a\nb\n', 'a    \n\nb')
