#
# Licensed to the Apache Software Foundation (ASF) under one or more
# contributor license agreements.  See the NOTICE file distributed with
# this work for additional information regarding copyright ownership.
# The ASF licenses this file to You under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with
# the License.  You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import unittest

from pyspark.sql.tests.streaming.test_streaming_foreachBatch import StreamingTestsForeachBatchMixin
from pyspark.testing.connectutils import ReusedConnectTestCase
from pyspark.errors import PySparkPicklingError


class StreamingForeachBatchParityTests(StreamingTestsForeachBatchMixin, ReusedConnectTestCase):
    @unittest.skip("SPARK-44463: Error handling needs improvement in connect foreachBatch")
    def test_streaming_foreachBatch_propagates_python_errors(self):
        super().test_streaming_foreachBatch_propagates_python_errors

    @unittest.skip("This seems specific to py4j and pinned threads. The intention is unclear")
    def test_streaming_foreachBatch_graceful_stop(self):
        super().test_streaming_foreachBatch_graceful_stop()

    # class StreamingForeachBatchParityTests(ReusedConnectTestCase):
    def test_accessing_spark_session(self):
        spark = self.spark

        def func(df, _):
            spark.createDataFrame([("do", "not"), ("serialize", "spark")]).collect()

        error_thrown = False
        try:
            self.spark.readStream.format("rate").load().writeStream.foreachBatch(func).start()
        except PySparkPicklingError as e:
            self.assertEqual(e.getErrorClass(), "STREAMING_CONNECT_SERIALIZATION_ERROR")
            error_thrown = True
        self.assertTrue(error_thrown)

    def test_accessing_spark_session_through_df(self):
        dataframe = self.spark.createDataFrame([("do", "not"), ("serialize", "dataframe")])

        def func(df, _):
            dataframe.collect()

        error_thrown = False
        try:
            self.spark.readStream.format("rate").load().writeStream.foreachBatch(func).start()
        except PySparkPicklingError as e:
            self.assertEqual(e.getErrorClass(), "STREAMING_CONNECT_SERIALIZATION_ERROR")
            error_thrown = True
        self.assertTrue(error_thrown)


if __name__ == "__main__":
    import unittest
    from pyspark.sql.tests.connect.streaming.test_parity_foreachBatch import *  # noqa: F401,E501

    try:
        import xmlrunner  # type: ignore[import]

        testRunner = xmlrunner.XMLTestRunner(output="target/test-reports", verbosity=2)
    except ImportError:
        testRunner = None
    unittest.main(testRunner=testRunner, verbosity=2)
