#
# Copyright (c) 2021, NVIDIA CORPORATION.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import pytest

tf4rec = pytest.importorskip("transformers4rec.tf")
tf = pytest.importorskip("tensorflow")


@pytest.mark.parametrize("dim", [32, 64])
@pytest.mark.parametrize("activation", ["relu", "tanh"])
@pytest.mark.parametrize("dropout", [None, 0.5])
@pytest.mark.parametrize(
    "normalization", [None, "batch_norm", tf.keras.layers.BatchNormalization()]
)
def test_mlp_block_yoochoose(
    yoochoose_schema, tf_yoochoose_like, dim, activation, dropout, normalization
):
    inputs = tf4rec.TabularFeatures.from_schema(yoochoose_schema, aggregation="concat")

    mlp = tf4rec.MLPBlock(
        [dim], activation=activation, dropout=dropout, normalization=normalization
    )
    body = tf4rec.SequentialBlock([inputs, mlp])

    outputs = body(tf_yoochoose_like)

    assert list(outputs.shape) == [100, dim]
    assert mlp.layers[0].units == dim
    assert mlp.layers[0].activation.__name__ == activation
    if dropout:
        assert mlp.layers[1].rate == dropout
    if normalization:
        if normalization == "batch_norm":
            normalization = tf.keras.layers.BatchNormalization()

        assert mlp.layers[-1].__class__.__name__ == normalization.__class__.__name__