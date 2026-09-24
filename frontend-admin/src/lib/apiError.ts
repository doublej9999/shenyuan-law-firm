/**
 * 统一解析后端接口错误，输出可直接展示给运营/律师用户的中文提示。
 * 尤其覆盖“后端版本落后于前端”的场景（缺少路由时 Django Ninja 返回 405）。
 */
export const describeDeleteError = (err: any): string => {
  const status = err?.response?.status

  if (status === 405) {
    return '后端服务尚未部署删除接口，请重新部署后端后再试'
  }
  if (status === 404) {
    return '该客户档案不存在，可能已被其他人删除'
  }
  if (status === 401) {
    return '登录状态已失效，请重新登录'
  }
  if (!err?.response) {
    return '无法连接后端服务，请检查网络后重试'
  }
  return err?.response?.data?.detail || '删除客户档案失败，请稍后重试'
}
