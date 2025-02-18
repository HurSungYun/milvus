import pytest

from base.client_v2_base import TestMilvusClientV2Base
from utils.util_log import test_log as log
from common import common_func as cf
from common import common_type as ct
from common.common_type import CaseLabel, CheckTasks
from utils.util_pymilvus import *

prefix = "client_index"
epsilon = ct.epsilon
default_nb = ct.default_nb
default_nb_medium = ct.default_nb_medium
default_nq = ct.default_nq
default_dim = ct.default_dim
default_limit = ct.default_limit
default_search_exp = "id >= 0"
exp_res = "exp_res"
default_search_string_exp = "varchar >= \"0\""
default_search_mix_exp = "int64 >= 0 && varchar >= \"0\""
default_invaild_string_exp = "varchar >= 0"
default_json_search_exp = "json_field[\"number\"] >= 0"
perfix_expr = 'varchar like "0%"'
default_search_field = ct.default_float_vec_field_name
default_search_params = ct.default_search_params
default_primary_key_field_name = "id"
default_vector_field_name = "vector"
default_multiple_vector_field_name = "vector_new"
default_float_field_name = ct.default_float_field_name
default_bool_field_name = ct.default_bool_field_name
default_string_field_name = ct.default_string_field_name
default_int32_array_field_name = ct.default_int32_array_field_name
default_string_array_field_name = ct.default_string_array_field_name


class TestMilvusClientIndexInvalid(TestMilvusClientV2Base):
    """ Test case of search interface """

    @pytest.fixture(scope="function", params=[False, True])
    def auto_id(self, request):
        yield request.param

    @pytest.fixture(scope="function", params=["COSINE", "L2"])
    def metric_type(self, request):
        yield request.param

    """
    ******************************************************************
    #  The following are invalid base cases
    ******************************************************************
    """

    @pytest.mark.tags(CaseLabel.L1)
    @pytest.mark.parametrize("name", ["12-s", "12 s", "(mn)", "中文", "%$#"])
    def test_milvus_client_index_invalid_collection_name(self, name):
        """
        target: test index abnormal case
        method: create index on invalid collection name
        expected: raise exception
        """
        client = self._client()
        collection_name = cf.gen_unique_str(prefix)
        # 1. create collection
        self.create_collection(client, collection_name, default_dim, consistency_level="Strong")
        self.release_collection(client, collection_name)
        self.drop_index(client, collection_name, "vector")
        # 2. prepare index params
        index_params = self.prepare_index_params(client)[0]
        index_params.add_index(field_name="vector")
        # 3. create index
        error = {ct.err_code: 1100, ct.err_msg: f"Invalid collection name: {name}. the first character of a collection "
                                                f"name must be an underscore or letter: invalid parameter"}
        self.create_index(client, name, index_params,
                          check_task=CheckTasks.err_res, check_items=error)
        self.drop_collection(client, collection_name)

    @pytest.mark.tags(CaseLabel.L1)
    @pytest.mark.parametrize("name", ["a".join("a" for i in range(256))])
    def test_milvus_client_index_collection_name_over_max_length(self, name):
        """
        target: test index abnormal case
        method: create index on collection name over max length
        expected: raise exception
        """
        client = self._client()
        collection_name = cf.gen_unique_str(prefix)
        # 1. create collection
        self.create_collection(client, collection_name, default_dim, consistency_level="Strong")
        self.release_collection(client, collection_name)
        self.drop_index(client, collection_name, "vector")
        # 2. prepare index params
        index_params = self.prepare_index_params(client)[0]
        index_params.add_index(field_name="vector")
        # 3. create index
        error = {ct.err_code: 1100, ct.err_msg: f"Invalid collection name: {name}. the length of a collection name "
                                                f"must be less than 255 characters: invalid parameter"}
        self.create_index(client, name, index_params,
                          check_task=CheckTasks.err_res, check_items=error)
        self.drop_collection(client, collection_name)

    @pytest.mark.tags(CaseLabel.L1)
    def test_milvus_client_index_not_exist_collection_name(self):
        """
        target: test index abnormal case
        method: create index on not exist collection name
        expected: raise exception
        """
        client = self._client()
        collection_name = cf.gen_unique_str(prefix)
        not_existed_collection_name = cf.gen_unique_str("not_existed_collection")
        # 1. create collection
        self.create_collection(client, collection_name, default_dim, consistency_level="Strong")
        self.release_collection(client, collection_name)
        self.drop_index(client, collection_name, "vector")
        # 2. prepare index params
        index_params = self.prepare_index_params(client)[0]
        index_params.add_index(field_name="vector")
        # 3. create index
        error = {ct.err_code: 100,
                 ct.err_msg: f"can't find collection[database=default][collection={not_existed_collection_name}]"}
        self.create_index(client, not_existed_collection_name, index_params,
                          check_task=CheckTasks.err_res, check_items=error)
        self.drop_collection(client, collection_name)

    @pytest.mark.tags(CaseLabel.L1)
    @pytest.mark.skip(reason="pymilvus issue 1885")
    @pytest.mark.parametrize("index", ["12-s", "12 s", "(mn)", "中文", "%$#", "a".join("a" for i in range(256))])
    def test_milvus_client_index_invalid_index_type(self, index):
        """
        target: test index abnormal case
        method: create index on invalid index type
        expected: raise exception
        """
        client = self._client()
        collection_name = cf.gen_unique_str(prefix)
        # 1. create collection
        self.create_collection(client, collection_name, default_dim, consistency_level="Strong")
        self.release_collection(client, collection_name)
        self.drop_index(client, collection_name, "vector")
        # 2. prepare index params
        index_params = self.prepare_index_params(client)[0]
        index_params.add_index(field_name="vector", index_type=index)
        # 3. create index
        error = {ct.err_code: 100, ct.err_msg: f"can't find collection collection not "
                                               f"found[database=default][collection=not_existed]"}
        self.create_index(client, collection_name, index_params,
                          check_task=CheckTasks.err_res, check_items=error)
        self.drop_collection(client, collection_name)

    @pytest.mark.tags(CaseLabel.L1)
    @pytest.mark.skip(reason="pymilvus issue 1885")
    @pytest.mark.parametrize("metric", ["12-s", "12 s", "(mn)", "中文", "%$#", "a".join("a" for i in range(256))])
    def test_milvus_client_index_invalid_metric_type(self, metric):
        """
        target: test index abnormal case
        method: create index on invalid metric type
        expected: raise exception
        """
        client = self._client()
        collection_name = cf.gen_unique_str(prefix)
        # 1. create collection
        self.create_collection(client, collection_name, default_dim, consistency_level="Strong")
        self.release_collection(client, collection_name)
        self.drop_index(client, collection_name, "vector")
        # 2. prepare index params
        index_params = self.prepare_index_params(client)[0]
        index_params.add_index(field_name="vector", metric_type=metric)
        # 3. create index
        error = {ct.err_code: 100, ct.err_msg: f"can't find collection collection not "
                                               f"found[database=default][collection=not_existed]"}
        self.create_index(client, collection_name, index_params,
                          check_task=CheckTasks.err_res, check_items=error)
        self.drop_collection(client, collection_name)

    @pytest.mark.tags(CaseLabel.L1)
    def test_milvus_client_index_drop_index_before_release(self):
        """
        target: test index abnormal case
        method: drop index before release
        expected: raise exception
        """
        client = self._client()
        collection_name = cf.gen_unique_str(prefix)
        # 1. create collection
        self.create_collection(client, collection_name, default_dim, consistency_level="Strong")
        error = {ct.err_code: 65535, ct.err_msg: f"index cannot be dropped, collection is loaded, "
                                                 f"please release it first"}
        self.drop_index(client, collection_name, "vector",
                        check_task=CheckTasks.err_res, check_items=error)
        self.drop_collection(client, collection_name)

    @pytest.mark.tags(CaseLabel.L1)
    def test_milvus_client_create_multiple_diff_index_without_release(self):
        """
        target: test index abnormal case
        method: create different index on one field without release
        expected: raise exception
        """
        client = self._client()
        collection_name = cf.gen_unique_str(prefix)
        # 1. create collection
        self.create_collection(client, collection_name, default_dim, consistency_level="Strong")
        # 2. prepare index params
        index_params = self.prepare_index_params(client)[0]
        index_params.add_index(field_name="vector", index_type="IVF_FLAT", metric_type="L2")
        # 3. create another index
        error = {ct.err_code: 65535, ct.err_msg: "CreateIndex failed: at most one distinct index is allowed per field"}
        self.create_index(client, collection_name, index_params,
                          check_task=CheckTasks.err_res, check_items=error)
        self.drop_collection(client, collection_name)


class TestMilvusClientIndexValid(TestMilvusClientV2Base):
    """ Test case of index interface """

    @pytest.fixture(scope="function", params=[False, True])
    def auto_id(self, request):
        yield request.param

    @pytest.fixture(scope="function", params=["COSINE", "L2", "IP"])
    def metric_type(self, request):
        yield request.param

    @pytest.fixture(scope="function", params=["TRIE", "STL_SORT", "INVERTED", "AUTOINDEX"])
    def scalar_index(self, request):
        yield request.param

    @pytest.fixture(scope="function", params=["TRIE", "INVERTED", "AUTOINDEX", ""])
    def varchar_index(self, request):
        yield request.param

    @pytest.fixture(scope="function", params=["STL_SORT", "INVERTED", "AUTOINDEX", ""])
    def numeric_index(self, request):
        yield request.param

    """
    ******************************************************************
    #  The following are valid base cases
    ******************************************************************
    """

    @pytest.mark.tags(CaseLabel.L1)
    @pytest.mark.skip("https://github.com/milvus-io/pymilvus/issues/1886")
    @pytest.mark.parametrize("index, params",
                             zip(ct.all_index_types[:7],
                                 ct.default_all_indexes_params[:7]))
    def test_milvus_client_index_default(self, index, params, metric_type):
        """
        target: test index normal case
        method: create connection, collection, create index, insert and search
        expected: index/search/query successfully
        """
        client = self._client()
        collection_name = cf.gen_unique_str(prefix)
        # 1. create collection
        self.create_collection(client, collection_name, default_dim, consistency_level="Strong")
        self.release_collection(client, collection_name)
        self.drop_index(client, collection_name, "vector")
        res = self.list_indexes(client, collection_name)[0]
        assert res == []
        # 2. prepare index params
        index_params = self.prepare_index_params(client)[0]
        index_params.add_index(field_name="vector", index_type=index, metric_type=metric_type)
        # 3. create index
        self.create_index(client, collection_name, index_params)
        # 4. create same index twice
        self.create_index(client, collection_name, index_params)
        # 5. insert
        rng = np.random.default_rng(seed=19530)
        rows = [{default_primary_key_field_name: i, default_vector_field_name: list(rng.random((1, default_dim))[0]),
                 default_float_field_name: i * 1.0, default_string_field_name: str(i)} for i in range(default_nb)]
        self.insert(client, collection_name, rows)
        # 6. load collection
        self.load_collection(client, collection_name)
        # 7. search
        vectors_to_search = rng.random((1, default_dim))
        insert_ids = [i for i in range(default_nb)]
        self.search(client, collection_name, vectors_to_search,
                    check_task=CheckTasks.check_search_results,
                    check_items={"enable_milvus_client_api": True,
                                 "nq": len(vectors_to_search),
                                 "ids": insert_ids,
                                 "limit": default_limit})
        # 8. query
        self.query(client, collection_name, filter=default_search_exp,
                   check_task=CheckTasks.check_query_results,
                   check_items={exp_res: rows,
                                "with_vec": True,
                                "primary_field": default_primary_key_field_name})
        self.drop_collection(client, collection_name)

    @pytest.mark.tags(CaseLabel.L2)
    @pytest.mark.parametrize("index, params",
                             zip(ct.all_index_types[:7],
                                 ct.default_all_indexes_params[:7]))
    def test_milvus_client_index_with_params(self, index, params, metric_type):
        """
        target: test index with user defined params
        method: create connection, collection, index, insert and search
        expected: index/search/query successfully
        """
        client = self._client()
        collection_name = cf.gen_unique_str(prefix)
        # 1. create collection
        self.create_collection(client, collection_name, default_dim, consistency_level="Strong")
        self.release_collection(client, collection_name)
        self.drop_index(client, collection_name, "vector")
        res = self.list_indexes(client, collection_name)[0]
        assert res == []
        # 2. prepare index params
        index_params = self.prepare_index_params(client)[0]
        index_params.add_index(field_name="vector", index_type=index, params=params, metric_type=metric_type)
        # 3. create index
        self.create_index(client, collection_name, index_params)
        # 4. insert
        rng = np.random.default_rng(seed=19530)
        rows = [{default_primary_key_field_name: i, default_vector_field_name: list(rng.random((1, default_dim))[0]),
                 default_float_field_name: i * 1.0, default_string_field_name: str(i)} for i in range(default_nb)]
        self.insert(client, collection_name, rows)
        # 5. load collection
        self.load_collection(client, collection_name)
        # 6. search
        vectors_to_search = rng.random((1, default_dim))
        insert_ids = [i for i in range(default_nb)]
        self.search(client, collection_name, vectors_to_search,
                    check_task=CheckTasks.check_search_results,
                    check_items={"enable_milvus_client_api": True,
                                 "nq": len(vectors_to_search),
                                 "ids": insert_ids,
                                 "limit": default_limit})
        # 7. query
        self.query(client, collection_name, filter=default_search_exp,
                   check_task=CheckTasks.check_query_results,
                   check_items={exp_res: rows,
                                "with_vec": True,
                                "primary_field": default_primary_key_field_name})
        self.drop_collection(client, collection_name)

    @pytest.mark.tags(CaseLabel.L2)
    @pytest.mark.parametrize("index, params",
                             zip(ct.all_index_types[:7],
                                 ct.default_all_indexes_params[:7]))
    def test_milvus_client_index_after_insert(self, index, params, metric_type):
        """
        target: test index after insert
        method: create connection, collection, insert, index and search
        expected: index/search/query successfully
        """
        client = self._client()
        collection_name = cf.gen_unique_str(prefix)
        # 1. create collection
        self.create_collection(client, collection_name, default_dim, consistency_level="Strong")
        self.release_collection(client, collection_name)
        self.drop_index(client, collection_name, "vector")
        # 2. insert
        rng = np.random.default_rng(seed=19530)
        rows = [{default_primary_key_field_name: i, default_vector_field_name: list(rng.random((1, default_dim))[0]),
                 default_float_field_name: i * 1.0, default_string_field_name: str(i)} for i in range(default_nb)]
        self.insert(client, collection_name, rows)
        # 3. prepare index params
        index_params = self.prepare_index_params(client)[0]
        index_params.add_index(field_name="vector", index_type=index, metric_type=metric_type, params=params)
        # 4. create index
        self.create_index(client, collection_name, index_params)
        # 5. load collection
        self.load_collection(client, collection_name)
        # 5. search
        vectors_to_search = rng.random((1, default_dim))
        insert_ids = [i for i in range(default_nb)]
        self.search(client, collection_name, vectors_to_search,
                    check_task=CheckTasks.check_search_results,
                    check_items={"enable_milvus_client_api": True,
                                 "nq": len(vectors_to_search),
                                 "ids": insert_ids,
                                 "limit": default_limit})
        # 4. query
        self.query(client, collection_name, filter=default_search_exp,
                   check_task=CheckTasks.check_query_results,
                   check_items={exp_res: rows,
                                "with_vec": True,
                                "primary_field": default_primary_key_field_name})
        self.drop_collection(client, collection_name)

    @pytest.mark.tags(CaseLabel.L2)
    def test_milvus_client_index_auto_index(self, numeric_index, varchar_index, metric_type):
        """
        target: test index with autoindex on both scalar and vector field
        method: create connection, collection, insert and search
        expected: index/search/query successfully
        """
        client = self._client()
        collection_name = cf.gen_unique_str(prefix)
        # 1. create collection
        schema = self.create_schema(client)[0]
        schema.add_field(default_primary_key_field_name, DataType.INT64, is_primary=True)
        schema.add_field(ct.default_int32_field_name, DataType.INT32)
        schema.add_field(ct.default_int16_field_name, DataType.INT16)
        schema.add_field(ct.default_int8_field_name, DataType.INT8)
        schema.add_field(default_string_field_name, DataType.VARCHAR, max_length=64)
        schema.add_field(default_float_field_name, DataType.FLOAT)
        schema.add_field(ct.default_double_field_name, DataType.DOUBLE)
        schema.add_field(ct.default_bool_field_name, DataType.BOOL)
        schema.add_field(default_vector_field_name, DataType.FLOAT_VECTOR, dim=default_dim)
        self.create_collection(client, collection_name, schema=schema, consistency_level="Strong")
        self.release_collection(client, collection_name)
        self.drop_index(client, collection_name, "vector")
        res = self.list_indexes(client, collection_name)[0]
        assert res == []
        # 2. prepare index params
        index = "AUTOINDEX"
        index_params = self.prepare_index_params(client)[0]
        index_params.add_index(field_name=default_vector_field_name, index_type=index, metric_type=metric_type)
        index_params.add_index(field_name=ct.default_int32_field_name, index_type=numeric_index, metric_type=metric_type)
        index_params.add_index(field_name=ct.default_int16_field_name, index_type=numeric_index, metric_type=metric_type)
        index_params.add_index(field_name=ct.default_int8_field_name, index_type=numeric_index, metric_type=metric_type)
        index_params.add_index(field_name=default_float_field_name, index_type=numeric_index, metric_type=metric_type)
        index_params.add_index(field_name=ct.default_double_field_name, index_type=numeric_index, metric_type=metric_type)
        index_params.add_index(field_name=ct.default_bool_field_name, index_type="", metric_type=metric_type)
        index_params.add_index(field_name=default_string_field_name, index_type=varchar_index, metric_type=metric_type)
        index_params.add_index(field_name=default_primary_key_field_name, index_type=numeric_index, metric_type=metric_type)
        # 3. create index
        self.create_index(client, collection_name, index_params)
        # 4. drop index
        self.drop_index(client, collection_name, default_vector_field_name)
        self.drop_index(client, collection_name, ct.default_int32_field_name)
        self.drop_index(client, collection_name, ct.default_int16_field_name)
        self.drop_index(client, collection_name, ct.default_int8_field_name)
        self.drop_index(client, collection_name, default_float_field_name)
        self.drop_index(client, collection_name, ct.default_double_field_name)
        self.drop_index(client, collection_name, ct.default_bool_field_name)
        self.drop_index(client, collection_name, default_string_field_name)
        self.drop_index(client, collection_name, default_primary_key_field_name)
        # 5. create index
        self.create_index(client, collection_name, index_params)
        # 6. insert
        rng = np.random.default_rng(seed=19530)
        rows = [{default_primary_key_field_name: i, default_vector_field_name: list(rng.random((1, default_dim))[0]),
                 ct.default_int32_field_name: np.int32(i), ct.default_int16_field_name: np.int16(i),
                 ct.default_int8_field_name: np.int8(i), default_float_field_name: i * 1.0,
                 ct.default_double_field_name: np.double(i), ct.default_bool_field_name: np.bool_(i),
                 default_string_field_name: str(i)} for i in range(default_nb)]
        self.insert(client, collection_name, rows)
        # 7. load collection
        self.load_collection(client, collection_name)
        # 8. search
        vectors_to_search = rng.random((1, default_dim))
        insert_ids = [i for i in range(default_nb)]
        self.search(client, collection_name, vectors_to_search,
                    check_task=CheckTasks.check_search_results,
                    check_items={"enable_milvus_client_api": True,
                                 "nq": len(vectors_to_search),
                                 "ids": insert_ids,
                                 "limit": default_limit})
        # 9. query
        self.query(client, collection_name, filter=default_search_exp,
                   check_task=CheckTasks.check_query_results,
                   check_items={exp_res: rows,
                                "with_vec": True,
                                "primary_field": default_primary_key_field_name})
        self.drop_collection(client, collection_name)

    @pytest.mark.tags(CaseLabel.L1)
    def test_milvus_client_scalar_hybrid_index_small_distinct_before_insert(self, metric_type):
        """
        target: test index with autoindex on int/varchar with small distinct value (<=100)
        method: create connection, collection, insert and search
        expected: index/search/query successfully (autoindex is bitmap index indeed)
        """
        client = self._client()
        collection_name = cf.gen_unique_str(prefix)
        # 1. create collection
        int64_field_name = "int"
        schema = self.create_schema(client)[0]
        schema.add_field(default_primary_key_field_name, DataType.INT64, is_primary=True)
        schema.add_field(default_string_field_name, DataType.VARCHAR, max_length=64)
        schema.add_field(int64_field_name, DataType.INT64)
        schema.add_field(default_vector_field_name, DataType.FLOAT_VECTOR, dim=default_dim)
        self.create_collection(client, collection_name, schema=schema, consistency_level="Strong")
        self.release_collection(client, collection_name)
        self.drop_index(client, collection_name, "vector")
        res = self.list_indexes(client, collection_name)[0]
        assert res == []
        # 2. prepare index params
        index = "AUTOINDEX"
        index_params = self.prepare_index_params(client)[0]
        index_params.add_index(field_name=default_vector_field_name, index_type=index, metric_type=metric_type)
        index_params.add_index(field_name=int64_field_name, index_type=index, metric_type=metric_type)
        index_params.add_index(field_name=default_string_field_name, index_type=index, metric_type=metric_type)
        # 3. create index
        self.create_index(client, collection_name, index_params)
        # 4. insert
        rng = np.random.default_rng(seed=19530)
        rows = [{default_primary_key_field_name: i, default_vector_field_name: list(rng.random((1, default_dim))[0]),
                 int64_field_name: np.random.randint(0, 99), default_string_field_name: str(np.random.randint(0, 99))}
                for i in range(default_nb)]
        self.insert(client, collection_name, rows)
        # 5. load collection
        self.load_collection(client, collection_name)
        # 6. search
        vectors_to_search = rng.random((1, default_dim))
        insert_ids = [i for i in range(default_nb)]
        self.search(client, collection_name, vectors_to_search,
                    check_task=CheckTasks.check_search_results,
                    check_items={"enable_milvus_client_api": True,
                                 "nq": len(vectors_to_search),
                                 "ids": insert_ids,
                                 "limit": default_limit})
        # 7. query
        self.query(client, collection_name, filter=default_search_exp,
                   check_task=CheckTasks.check_query_results,
                   check_items={exp_res: rows,
                                "with_vec": True,
                                "primary_field": default_primary_key_field_name})
        self.drop_collection(client, collection_name)

    @pytest.mark.tags(CaseLabel.L1)
    def test_milvus_client_scalar_hybrid_index_small_to_large_distinct_after_insert(self, metric_type):
        """
        target: test index with autoindex on int/varchar with small distinct value (<=100) first and
                insert to large distinct (2000+) later
        method: create connection, collection, insert and search
        expected: index/search/query successfully
        """
        client = self._client()
        collection_name = cf.gen_unique_str(prefix)
        # 1. create collection
        int64_field_name = "int"
        schema = self.create_schema(client)[0]
        schema.add_field(default_primary_key_field_name, DataType.INT64, is_primary=True)
        schema.add_field(ct.default_int32_field_name, DataType.INT32)
        schema.add_field(ct.default_int16_field_name, DataType.INT16)
        schema.add_field(ct.default_int8_field_name, DataType.INT8)
        schema.add_field(default_string_field_name, DataType.VARCHAR, max_length=64)
        schema.add_field(int64_field_name, DataType.INT64)
        schema.add_field(default_vector_field_name, DataType.FLOAT_VECTOR, dim=default_dim)
        self.create_collection(client, collection_name, schema=schema, consistency_level="Strong")
        self.release_collection(client, collection_name)
        self.drop_index(client, collection_name, "vector")
        res = self.list_indexes(client, collection_name)[0]
        assert res == []
        # 2. insert
        rng = np.random.default_rng(seed=19530)
        rows = [{default_primary_key_field_name: i, default_vector_field_name: list(rng.random((1, default_dim))[0]),
                 int64_field_name: np.random.randint(0, 99), ct.default_int32_field_name: np.int32(i),
                 ct.default_int16_field_name: np.int16(i), ct.default_int8_field_name: np.int8(i),
                 default_string_field_name: str(np.random.randint(0, 99))} for i in range(default_nb)]
        self.insert(client, collection_name, rows)
        # 3. prepare index params
        index = "AUTOINDEX"
        index_params = self.prepare_index_params(client)[0]
        index_params.add_index(field_name=default_vector_field_name, index_type=index, metric_type=metric_type)
        index_params.add_index(field_name=int64_field_name, index_type=index, metric_type=metric_type)
        index_params.add_index(field_name=ct.default_int32_field_name, index_type="", metric_type=metric_type)
        index_params.add_index(field_name=ct.default_int16_field_name, metric_type=metric_type)
        index_params.add_index(field_name=ct.default_int8_field_name, index_type=index, metric_type=metric_type)
        index_params.add_index(field_name=default_string_field_name, index_type=index, metric_type=metric_type)
        # 4. create index
        self.create_index(client, collection_name, index_params)
        # 5. load collection
        self.load_collection(client, collection_name)
        # 6. search
        vectors_to_search = rng.random((1, default_dim))
        insert_ids = [i for i in range(default_nb)]
        self.search(client, collection_name, vectors_to_search,
                    check_task=CheckTasks.check_search_results,
                    check_items={"enable_milvus_client_api": True,
                                 "nq": len(vectors_to_search),
                                 "ids": insert_ids,
                                 "limit": default_limit})
        # 7. query
        self.query(client, collection_name, filter=default_search_exp,
                   check_task=CheckTasks.check_query_results,
                   check_items={exp_res: rows,
                                "with_vec": True,
                                "primary_field": default_primary_key_field_name})
        # 8. insert more distinct value to the scalar field to make the autoindex change
        rng = np.random.default_rng(seed=19530)
        rows = [{default_primary_key_field_name: i, default_vector_field_name: list(rng.random((1, default_dim))[0]),
                 int64_field_name: np.random.randint(0, 99), ct.default_int32_field_name: np.int32(i),
                 ct.default_int16_field_name: np.int16(i), ct.default_int8_field_name: np.int8(i),
                 default_string_field_name: str(np.random.randint(0, 99))} for i in range(default_nb, 2*default_nb)]
        self.insert(client, collection_name, rows)
        self.flush(client, collection_name)
        # 9. search
        vectors_to_search = rng.random((1, default_dim))
        insert_ids = [i for i in range(2*default_nb)]
        self.search(client, collection_name, vectors_to_search,
                    check_task=CheckTasks.check_search_results,
                    check_items={"enable_milvus_client_api": True,
                                 "nq": len(vectors_to_search),
                                 "ids": insert_ids,
                                 "limit": default_limit})
        self.drop_collection(client, collection_name)

    @pytest.mark.tags(CaseLabel.L2)
    def test_milvus_client_index_multiple_vectors(self, numeric_index, metric_type):
        """
        target: test index for multiple vectors
        method: create connection, collection, index, insert and search
        expected: index/search/query successfully
        """
        client = self._client()
        collection_name = cf.gen_unique_str(prefix)
        # 1. create collection
        self.create_collection(client, collection_name, default_dim, consistency_level="Strong")
        self.release_collection(client, collection_name)
        self.drop_index(client, collection_name, "vector")
        res = self.list_indexes(client, collection_name)[0]
        assert res == []
        # 2. prepare index params
        index = "AUTOINDEX"
        index_params = self.prepare_index_params(client)[0]
        index_params.add_index(field_name="vector", index_type=index, metric_type=metric_type)
        index_params.add_index(field_name="id", index_type=numeric_index, metric_type=metric_type)
        # 3. create index
        self.create_index(client, collection_name, index_params)
        # 4. insert
        rng = np.random.default_rng(seed=19530)
        rows = [{default_primary_key_field_name: i, default_vector_field_name: list(rng.random((1, default_dim))[0]),
                 default_float_field_name: i * 1.0, default_string_field_name: str(i),
                 default_multiple_vector_field_name: list(rng.random((1, default_dim))[0])} for i in range(default_nb)]
        self.insert(client, collection_name, rows)
        # 5. load collection
        self.load_collection(client, collection_name)
        # 6. search
        vectors_to_search = rng.random((1, default_dim))
        insert_ids = [i for i in range(default_nb)]
        self.search(client, collection_name, vectors_to_search,
                    check_task=CheckTasks.check_search_results,
                    check_items={"enable_milvus_client_api": True,
                                 "nq": len(vectors_to_search),
                                 "ids": insert_ids,
                                 "limit": default_limit})
        # 7. query
        self.query(client, collection_name, filter=default_search_exp,
                   check_task=CheckTasks.check_query_results,
                   check_items={exp_res: rows,
                                "with_vec": True,
                                "primary_field": default_primary_key_field_name})
        self.drop_collection(client, collection_name)

    @pytest.mark.tags(CaseLabel.L2)
    @pytest.mark.parametrize("index, params",
                             zip(ct.all_index_types[:7],
                                 ct.default_all_indexes_params[:7]))
    def test_milvus_client_index_drop_create_same_index(self, index, params, metric_type):
        """
        target: test index after drop and create same index twice
        method: create connection, collection, create/drop/create index, insert and search
        expected: index create/drop and search/query successfully
        """
        client = self._client()
        collection_name = cf.gen_unique_str(prefix)
        # 1. create collection
        self.create_collection(client, collection_name, default_dim, consistency_level="Strong")
        self.release_collection(client, collection_name)
        self.drop_index(client, collection_name, "vector")
        res = self.list_indexes(client, collection_name)[0]
        assert res == []
        # 2. prepare index params
        index_params = self.prepare_index_params(client)[0]
        index_params.add_index(field_name="vector", index_type=index, params=params, metric_type=metric_type)
        # 3. create index
        self.create_index(client, collection_name, index_params)
        # 4. drop index
        self.drop_index(client, collection_name, "vector")
        # 4. create same index twice
        self.create_index(client, collection_name, index_params)
        # 5. insert
        rng = np.random.default_rng(seed=19530)
        rows = [{default_primary_key_field_name: i, default_vector_field_name: list(rng.random((1, default_dim))[0]),
                 default_float_field_name: i * 1.0, default_string_field_name: str(i)} for i in range(default_nb)]
        self.insert(client, collection_name, rows)
        # 6. load collection
        self.load_collection(client, collection_name)
        # 7. search
        vectors_to_search = rng.random((1, default_dim))
        insert_ids = [i for i in range(default_nb)]
        self.search(client, collection_name, vectors_to_search,
                    check_task=CheckTasks.check_search_results,
                    check_items={"enable_milvus_client_api": True,
                                 "nq": len(vectors_to_search),
                                 "ids": insert_ids,
                                 "limit": default_limit})
        # 8. query
        self.query(client, collection_name, filter=default_search_exp,
                   check_task=CheckTasks.check_query_results,
                   check_items={exp_res: rows,
                                "with_vec": True,
                                "primary_field": default_primary_key_field_name})
        self.drop_collection(client, collection_name)

    @pytest.mark.tags(CaseLabel.L2)
    @pytest.mark.parametrize("index, params",
                             zip(ct.all_index_types[:7],
                                 ct.default_all_indexes_params[:7]))
    def test_milvus_client_index_drop_create_different_index(self, index, params, metric_type):
        """
        target: test index after drop and create different index twice
        method: create connection, collection, create/drop/create index, insert and search
        expected: index create/drop and search/query successfully
        """
        client = self._client()
        collection_name = cf.gen_unique_str(prefix)
        # 1. create collection
        self.create_collection(client, collection_name, default_dim, consistency_level="Strong")
        self.release_collection(client, collection_name)
        self.drop_index(client, collection_name, "vector")
        res = self.list_indexes(client, collection_name)[0]
        assert res == []
        # 2. prepare index params
        index_params = self.prepare_index_params(client)[0]
        index_params.add_index(field_name="vector", metric_type=metric_type)
        # 3. create index
        self.create_index(client, collection_name, index_params)
        # 4. drop index
        self.drop_index(client, collection_name, "vector")
        # 4. create different index
        index_params.add_index(field_name="vector", index_type=index, params=params, metric_type=metric_type)
        self.create_index(client, collection_name, index_params)
        # 5. insert
        rng = np.random.default_rng(seed=19530)
        rows = [{default_primary_key_field_name: i, default_vector_field_name: list(rng.random((1, default_dim))[0]),
                 default_float_field_name: i * 1.0, default_string_field_name: str(i)} for i in range(default_nb)]
        self.insert(client, collection_name, rows)
        # 6. load collection
        self.load_collection(client, collection_name)
        # 7. search
        vectors_to_search = rng.random((1, default_dim))
        insert_ids = [i for i in range(default_nb)]
        self.search(client, collection_name, vectors_to_search,
                    check_task=CheckTasks.check_search_results,
                    check_items={"enable_milvus_client_api": True,
                                 "nq": len(vectors_to_search),
                                 "ids": insert_ids,
                                 "limit": default_limit})
        # 8. query
        self.query(client, collection_name, filter=default_search_exp,
                   check_task=CheckTasks.check_query_results,
                   check_items={exp_res: rows,
                                "with_vec": True,
                                "primary_field": default_primary_key_field_name})
        self.drop_collection(client, collection_name)
