import axios, { AxiosResponse } from 'axios';

import AppConfig from 'config/config';
import { ResourceType } from 'interfaces';

import { DashboardSearchResults, TableSearchResults, UserSearchResults } from '../types';

import { ResourceFilterReducerState } from '../filters/reducer';

export const BASE_URL = '/api/search/v0';

export interface SearchAPI {
  msg: string;
  status_code: number;
  search_term: string;
  dashboards?: DashboardSearchResults;
  tables?: TableSearchResults;
  users?: UserSearchResults;
};

export const searchResourceHelper = (response: AxiosResponse<SearchAPI>) => {
  const { data } = response;
  const ret = { searchTerm: data.search_term };
  ['tables', 'users'].forEach((key) => {
    if (data[key]) {
      ret[key] = data[key];
    }
  });
  return ret;
};

export function searchResource(pageIndex: number, resource: ResourceType, term: string, filters: ResourceFilterReducerState = {}) {
  if (resource === ResourceType.dashboard ||
     (resource === ResourceType.user && !AppConfig.indexUsers.enabled)) {
    return Promise.resolve({});
  }
  if (Object.keys(filters).length > 0) {
    return axios.post(`${BASE_URL}/${resource}_qs`, {
      filters,
      term,
      pageIndex
    }).then(searchResourceHelper);
  }
  return axios.get(`${BASE_URL}/${resource}?query=${term}&page_index=${pageIndex}`)
    .then(searchResourceHelper);
};
